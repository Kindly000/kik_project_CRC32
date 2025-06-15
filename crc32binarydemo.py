def toBin(num):
    """
    Zamienia liczbę całkowitą na jej binarną reprezentację bez prefiksu '0b'.

    Args:
        num (int): Liczba całkowita.

    Returns:
        str: Binarny string (bez '0b' na początku), np. "1010".
    """
    return bin(num)[2:] if num != 0 else "0"


def toDec(bin_str):
    """
    Konwertuje ciąg binarny na liczbę całkowitą (dziesiętną).

    Args:
        bin_str (str): Ciąg bitów (np. "1011").

    Returns:
        int: Wartość dziesiętna liczby binarnej.
    """
    return int(bin_str, 2) if bin_str else 0


def CRC_visual(data, key):
    """
    Wizualizuje proces dzielenia binarnego przy obliczaniu kodu CRC.

    Dane są dzielone przez wielomian generujący w postaci binarnej (modulo 2).
    Na końcu zwracany jest codeword = dane + CRC.

    Args:
        data (str): Dane wejściowe jako ciąg binarny (np. "1011001").
        key (str): Wielomian generujący (np. "1001").

    Returns:
        str: Codeword (dane + CRC) jako ciąg binarny.

    Kluczowe linie i ich znaczenie:

    - `dividend = code << (n - 1)`:
        Przesuwa dane w lewo o n-1 bitów, czyli dodaje odpowiednią liczbę zer na końcu,
        by zostawić miejsce na resztę CRC.

    - `portion = dividend >> current_shft`:
        Pobiera najstarsze n bitów z aktualnego dividend do operacji XOR.

    - `rem = portion ^ gen`:
        Wykonuje operację XOR między aktualnym fragmentem danych a wielomianem generującym.

    - `dividend = (dividend & ((1 << current_shft) - 1)) | (rem << current_shft)`:
        Kluczowa linia symulująca „dzielenie w słupku”:
            - `(1 << current_shft) - 1` tworzy maskę z samymi jedynkami do pozycji current_shft.
            - `dividend & mask` usuwa n-bitowy fragment z przodu.
            - `rem << current_shft` wstawia z powrotem wynik XOR (czyli „resztę”) na to samo miejsce.
        To odzwierciedla operację dzielenia modulo 2 w CRC.

    - `toBin(dividend).zfill(total_bits)`:
        Zapewnia, że liczba binarna ma stałą długość, co jest pomocne w wizualizacji procesu.
    """

    print("🔍 Wizualizacja obliczania CRC:\n")

    n = len(key)
    if n == 0:
        print("Error: Key cannot be empty")
        return

    gen = toDec(key)
    code = toDec(data)
    data_len = len(data)
    max_shift = 0

    """Dodajemy n ( długość_wielomianu_generującego - 1 ) do ciągu danych -> przygotowujemy miejsce pod reszte"""
    dividend = code << (n - 1)
    total_bits = data_len + n - 1

    print(f"Wejściowe dane:    {data}")
    print(f"Generator (key):   {key}")
    print(f"Dane + zera:       {toBin(dividend).zfill(total_bits)}")
    print(f"Rozpoczynam dzielenie binarne...\n")

    while True:
        """Sprawdzamy czy aktualny dividend jest dłuższy niż wartość wielomiana generującego ( przez który jest on dzielony )"""
        current_shft = dividend.bit_length() - n
        if current_shft > max_shift:
            max_shift = current_shft
        if current_shft < 0:
            break

        """Bierzemy n najbardziej znaczących bitów z ciagu informacyjnego w celu XOR z wielomianem generujacym"""
        portion = dividend >> current_shft
        """W celach wizualizacji"""
        portion_bin = toBin(portion).zfill(n)
        gen_bin = toBin(gen).zfill(n)
        """Wykonuje XOR n-najbardziej znaczacych bitow z ciagu informacyjnego z wielomianem generujacym"""
        rem = portion ^ gen
        """W celach wizualizacji"""
        rem_bin = toBin(rem).zfill(n)

        dividend_bin = toBin(dividend).zfill(total_bits)

        start_idx = total_bits - dividend.bit_length() # gdzie zaczynaja sie znaczace bity ( bez zer na początku )
        portion_start = start_idx
        portion_end = portion_start + n  # n bitów, które bierzemy do XOR

        colored_dividend = (
            dividend_bin[:portion_start]
            + f"\033[32m{dividend_bin[portion_start:portion_end]}\033[0m"
            + dividend_bin[portion_end:]
        )


        print(f"Divident bits : {colored_dividend}")
        print(f"  XORing:       {portion_bin}")
        print(f"          XOR   {gen_bin}")
        print(f"        =       {rem_bin}")
        print(f"Posuwam się dalej w prawo (shift = {current_shft})\n")

        """Wstawiamy reszte z dzielenia na miejscu pierwszych n bitów w ciagu informacyjnym ( umitacja dzielenia w słupku )"""
        dividend = (dividend & ((1 << current_shft) - 1)) | (rem << current_shft)

    """Ostateczne wyniki"""
    remainder = dividend
    codeword = (code << (n - 1)) | remainder

    print("🔚 Koniec dzielenia.")
    print(f"🔸 Reszta (CRC):     {toBin(remainder).zfill(n - 1)}")
    print(f"🔸 Codeword (dane + CRC): {toBin(codeword).zfill(total_bits)}\n")

    return toBin(codeword)


def check_crc(codeword, key):
    """
    Sprawdza poprawność odebranego ciągu binarnego (codeword) za pomocą wielomianu CRC.

    Args:
        codeword (str): Odebrane dane + CRC (ciąg binarny).
        key (str): Wielomian generujący CRC (ciąg binarny).

    Nie zwraca wartości, ale wypisuje:
        - resztę z dzielenia (jeśli 0 → brak błędów),
        - komunikat czy CRC check się powiódł.

    Kluczowe linie:

    - `current_shft = dividend.bit_length() - n`:
        Sprawdza, czy dividend zawiera wystarczającą liczbę bitów do kolejnego dzielenia.

    - `rem = (dividend >> current_shft) ^ gen`:
        Pobiera fragment danych do dzielenia i wykonuje XOR z wielomianem.

    - `dividend = (dividend & ((1 << current_shft) - 1)) | (rem << current_shft)`:
        Analogicznie jak w `CRC_visual`, aktualizuje dividend po każdej iteracji XOR.

    - Na końcu:
        Jeśli dividend == 0 → oznacza, że nie było błędów transmisji (CRC passed).
        Inaczej → błąd został wykryty.
    """

    print("🔍 Sprawdzanie poprawności odebranego kodu...\n")

    n = len(key)
    gen = toDec(key)
    code = toDec(codeword)
    dividend = code

    while True:
        current_shft = dividend.bit_length() - n
        if current_shft < 0:
            break
        rem = (dividend >> current_shft) ^ gen
        dividend = (dividend & ((1 << current_shft) - 1)) | (rem << current_shft)

    print(f"Reszta po sprawdzeniu: {toBin(dividend)}")
    if dividend == 0:
        print("✅ CRC check passed: brak błędów.")
    else:
        print("❌ CRC check failed: wykryto błąd.")


if __name__ == "__main__":
    """
    Funkcja główna programu demonstracyjnego CRC.

    - Inicjalizuje dane binarne wejściowe.
    - Ustawia 33-bitowy wielomian generujący CRC.
    - Oblicza codeword (data + CRC).
    - Sprawdza poprawność przesyłu przy użyciu kodu CRC.
    """
    data = "00111010001100101011100110111010010001110100011110010100011010"
    generator_hex = "0x04C11DB7"
    generator_bin = bin(int(generator_hex, 16))[2:].zfill(32)
    generator_bin = "1" + generator_bin  # upewniamy się, że jest 33-bitowy

    """Do testow"""
    # data = "1000101"
    # generator_bin = "101"

    print("-" * 10 + " CRC wizualizacja z 802.3/802.11 polynomem " + "-" * 10)
    print(f"Generator G(x): {generator_bin}")
    print("-" * 60)

    check = data + "11001010000100100111111101101111"

    # codeword = CRC_visual(data, generator_bin)
    check_crc(check, generator_bin)
