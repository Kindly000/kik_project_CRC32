# Raport: Implementacja kodu wielomianowego CRC-32 – IEEE 802.3

**Autorzy:** Antoni Lenart, Bruno Banaszczyk, Jakub Kowalski, Filip Kaczor, Jakub Kogut  
**Data:** 15 czerwca 2025

## 1. Wprowadzenie

Kody CRC (Cyclic Redundancy Check) są powszechnie stosowaną metodą wykrywania błędów w transmisji danych oraz przechowywaniu informacji w systemach cyfrowych. Projekt koncentruje się na implementacji kodu CRC-32 zgodnego ze standardem IEEE 802.3, wykorzystywanym m\.in. w sieciach Ethernet. Niniejszy raport przedstawia szczegółowy opis podstaw matematycznych, algorytmu, implementacji w języku Python, dokumentację kodu, wyniki jego działania oraz miejsce na przedstawienie sprzętowej implementacji w programie MultiSim.

Celem projektu jest analiza i implementacja CRC-32, omówienie jego zastosowań, możliwości detekcyjnych oraz stworzenie wizualizacji procesu obliczania sumy kontrolnej. Projekt obejmuje zarówno aspekty teoretyczne, jak i praktyczne, w tym symulację działania algorytmu oraz potencjalną implementację sprzętową.

---

## 2. Teoretyczne podstawy CRC

### 2.1. Czym jest CRC?

CRC to technika wykrywania błędów polegająca na dołączaniu do bloku danych krótkiej wartości kontrolnej, będącej resztą z dzielenia wielomianowego zawartości danych. Po stronie odbiorczej obliczenia są powtarzane, a niezgodność wartości kontrolnych wskazuje na uszkodzenie danych. Nazwa CRC pochodzi od:
- **Redundancji**: wartość kontrolna zwiększa rozmiar wiadomości bez dodawania nowych informacji.
- **Cykliczności**: operacje są oparte na kodach wielomianowych.

CRC jest popularne ze względu na:
- Prostą implementację sprzętową.
- Łatwość analizy matematycznej.
- Wysoką skuteczność w wykrywaniu błędów spowodowanych szumami w kanałach transmisyjnych.

### 2.2. Zastosowania CRC

Kody CRC znajdują zastosowanie w wielu dziedzinach, m\.in.:
- **Sieci komputerowe**: Ethernet (IEEE 802.3), WiFi (IEEE 802.11).
- **Systemy komunikacji**: CAN, USB, Bluetooth.
- **Przechowywanie danych**: dyski twarde, SSD.
- **Formaty plików i kompresja**: ZIP, RAR, Gzip, PNG.
- **Funkcje hashujące**: rzadziej, w specyficznych zastosowaniach.

### 2.3. Podstawy matematyczne CRC-32

CRC-32 opiera się na arytmetyce wielomianów w ciele skończonym GF(2), gdzie:
- Dodawanie i odejmowanie to operacja XOR.
- Mnożenie i dzielenie są specyficzne dla arytmetyki binarnej.

Wiadomości są reprezentowane jako wielomiany $ M(x) $, gdzie każdy bit odpowiada współczynnikowi. Na przykład ciąg bitów `1011` odpowiada wielomianowi $ x^3 + x + 1 $.

#### Wielomian generujący
Standardowy wielomian generujący dla CRC-32 (IEEE 802.3) to:\
$ G(x) = x^{32} + x^{26} + x^{23} + x^{22} + x^{16} + x^{12} + x^{11} + x^{10} + x^8 + x^7 + x^5 + x^4 + x^2 + x + 1 $\
W postaci binarnej: `100000100110000010001110110110111` (33 bity, w tym bit najwyższego stopnia).

#### Proces obliczania CRC
1. **Dopełnienie danych**: Dane wejściowe są mnożone przez $ x^{32} $, co odpowiada dopełnieniu 32 zerami na końcu.\
$ M'(x) = M(x) \cdot x^{32}$
2. **Dzielenie wielomianowe**: Dopełnione dane są dzielone przez $ G(x) $ w ciele GF(2). Reszta z dzielenia (32 bity) stanowi sumę kontrolną CRC.
$ M'(x) = Q(x) \cdot G(x) + R(x) ,\; deg(R(x)) < 32 $
3. **Dołączanie sumy kontrolnej**: Reszta $ R(x) $ jest dołączana do oryginalnych danych, tworząc słowo kodowe.
4. **Weryfikacja**: Odbiorca dzieli otrzymane słowo $ M'(x) $ kodowe przez $ G(x) $. Jeśli reszta wynosi 0, dane są poprawne.\
$ M'(x)\;mod\;G(x) = 0$

#### Projektowanie wielomianu generującego
Wielomian $ G(x) $ musi być starannie wybrany, aby zapewnić wysoką skuteczność wykrywania błędów. Kluczowe cechy:
- **Wielomian pierwotny**: ma on największy "cykl" wykrywalności. Wykrywa: wszystkie 1-bitowe błędy, wszystkie 2-bitowe błędy jeśli blok_danych $\le 2^{r} - 1$, gdzie `r` to stopień wielomianu.
Nie mamy natomiast gwarancji wykrycia wszystkich błędów 3-bitowych, 4-bitowych itd. 
- **Wielomian typu $ g(x) = p(x) \cdot (x+1) $** , $p(x) \to $ pierwiastek pierwotny stopnia `(r-1)`: Wykrywa wszystki błędy 1-bitowe, 2-bitowe oraz wszystkie błędy o nieparzystej liczbie błędów.
Ma on natomiast krótszy maksymalny blok danych, w którym można wykryć błąd: $ 2^{r-1} - 1$, czyli o połowe mniej niż w przypadku pierwotnego wielomianu generującego.
- **Wielomiany rozkładalne**: Wielomian jest rozkładalny, jeśli da się go zapisać w następujący sposób:\
$ g(x) = f(x) \cdot h(x) $\
W takiej sytuacji pierścień resztkowy nie jest ciałem, tylko ma w sobie tzw. zero-dzielniki. Są to takie elementy $a(x)$, dla których istnieje element niezerowy $b(x)$, taki że:\
$a(x) \cdot b(x) = 0 \; mod \; g(x)$\
Jeżeli jakikolwiek błąd przyjmie taką właśnie postać, to nie będziemy w stanie go wykryć za pomocą CRC. 
#### Możliwości detekcyjne CRC
Jeśli dane zostaną zmienione ( np. przez zakłócenia transmisji ), to odebrany ciąg będzie różnił się od oryginału. Tę różnicę zapisuje się jako wielomian błędu $E(x)$. CRC będzie w stanie wykryć błąd tylko wtedy, gdy $E(x)$ nie dzieli się przez $G(x)$.

Jakie jesteśmy w stanie wykryć z pomocą kodów cyklicznych CRC-x ?
- **Błędy pojedynczego bitu**: Zawsze, jeśli $ G(x) $ ma co najmniej dwa niezerowe wyrazy.
Wyjaśnienie:\
$E(x) = x^{5} \to$ wielomian $x^{k}$ dzieli się tylko przez $x, x^{2}, x^{3}, \ldots$ (wielomiany tylko z jednym współczynnikiem)
- **Błędy dwóch bitów**: Jeśli odległość między błędnymi bitami jest mniejsza niż rząd wielomianu pierwotnego.
Czym jest rząd wielomianu ?\
Jest to najmniejsza liczba `m`, dla której:\
$ G(x) | (x^{m} + 1)$\
Wyjaśnienie:\
$E(x) = x^{k}\cdot(x^{i-k}+1) \to$ widzimy, że $G(x)$ musi dzielić $x^{i-k}+1$ żeby nie było możliwe wykrycie tego błędu.
- **Błędy o nieparzystej liczbie bitów**: Jeśli $ G(x) $ jest podzielny przez $ (x+1) $.
Wyjaśnienie:\
Dany wielomian $f(x)$ jest podzielny przez $(x+1)$ jeśli jego wartość w punkcie 1 wynosi 0, czyli:\
$f(1)=0 \leftrightarrow x+1\;|\;f(x)$\
Zgodnie z zasadami arytmetyki w ciele $GF(2)$ sumowanie nieparzystej liczby 1 daje nam wynik $\to$ 1 ( wystąpienie błędu ), natomiast parzysta liczba 1 w $E(x)$ daje pozorny brak błędu ( oczywiście jest to błędne wskazanie ).
- **Błędy burst**: Ciągłe sekwencje błędnych bitów o długości mniejszej niż stopień $ G(x) $, jeśli najwyższy współczynnik i wyraz wolny są niezerowe.
Wyjaśnienie:\
Błąd burst jest to taki błąd, który występuje w postaci ciągłej sekwencji błędnych bitów, w której:
  * pierwszy i ostatni bit są błędne
  * pomiędzy nimi może znajdować się dowolna liczba ( również 0 ) błędnych lub poprawnych błędów.
- **Wszystkie kombinacje błędów mniejszych niż minimalna odległość Hamminga**: 
Wyjaśnienie:\
Minimalna odległość Hamminga kodu $\to$ czyli najmniejsza liczba bitów, które trzeba zmienić, aby otrzymać inne słowo kodowe.\
Błędy o liczności < $d_{min}$ nie są w stanie przekształcić poprawnego słowa kodowego w inne poprawne słowo kodowe. Czyli takie słowo zostanie wykryte jako nieprawidłowe.

Problemy z wykrywaniem:
- **Błędy na początku sekwencji (zera na początku).**
- **Błędy o parzystej liczbie bitów, jeśli $ G(x) $ nie zawiera $ (x+1) $**.

---

## 3. Algorytm CRC-32

Algorytm CRC-32 według standardu IEEE 802.3 (zdefiniowany w IEEE 802.3 - 2022 ) polega na:
1. Przyjęciu danych wejściowych jako ciągu bitów.
2. Dopełnieniu danych 32 zerami.
3. Wykonaniu dzielenia wielomianowego przez wielomian generujący.
4. Dołączeniu 32-bitowej reszty jako sumy kontrolnej.
5. Weryfikacji po stronie odbiorcy przez powtórzenie dzielenia.

[802-3-CRC32](https://i.sstatic.net/aVTur.png)

---

## 4. Implementacja w Pythonie

### 4.1. Dokumentacja kodu

#### Spis treści
- [Wprowadzenie](#wprowadzenie)
- [Funkcje](#funkcje)
  - [toBin(num)](#tobin-num)
  - [toDec(bin_str)](#todec-bin_str)
  - [CRC_visual(data, key)](#crc_visual-data-key)
  - [check_crc(codeword, key)](#check_crc-codeword-key)

#### Wprowadzenie
Dokumentacja opisuje implementację algorytmu CRC-32 w Pythonie, zgodnego ze standardem IEEE 802.3. Kod zawiera funkcje do obliczania sumy kontrolnej CRC, wizualizacji procesu dzielenia binarnego oraz weryfikacji poprawności danych. Każda funkcja jest opisana pod kątem jej przeznaczenia, parametrów, zwracanych wartości oraz kluczowych fragmentów kodu.

#### Funkcje

##### toBin(num)
Konwertuje liczbę całkowitą na ciąg binarny, usuwając prefiks `0b`.

###### Parametry
- `num` (int): Liczba całkowita do konwersji.

###### Zwraca
- `str`: Ciąg binarny reprezentujący liczbę. Dla zera zwraca `"0"`.

###### Przykład

```python
>>> toBin(10)
'1010'
>>> toBin(0)
'0'
```

###### Kluczowe linie kodu

```python
return bin(num)[2:] if num != 0 else "0"
```

- **`bin(num)[2:]`**: Konwertuje liczbę na ciąg binarny i usuwa prefiks `0b`.
- **Warunek `if num != 0 else "0"`**: Zapewnia, że dla zera zwracany jest ciąg `"0"`.

---

##### toDec(bin_str)
Konwertuje ciąg binarny na liczbę całkowitą (dziesiętną).

###### Parametry
- `bin_str` (str): Ciąg binarny (np. `"1011"`).

###### Zwraca
- `int`: Wartość dziesiętna odpowiadająca ciągowi binarnemu. Dla pustego ciągu zwraca `0`.

###### Przykład

```python
>>> toDec("1011")
11
>>> toDec("")
0
```

###### Kluczowe linie kodu

```python
return int(bin_str, 2) if bin_str else 0
```

- **`int(bin_str, 2)`**: Konwertuje ciąg binarny na liczbę dziesiętną.
- **Warunek `if bin_str else 0`**: Obsługuje pusty ciąg, zwracając `0`.

---

##### CRC_visual(data, key)
Wizualizuje proces obliczania sumy kontrolnej CRC-32 poprzez dzielenie binarne w ciele GF(2). Dane są dzielone przez wielomian generujący, a wynik (słowo kodowe) zawiera dane wejściowe i dołączoną sumę kontrolną.

###### Parametry
- `data` (str): Ciąg binarny reprezentujący dane wejściowe (np. `"1011001"`).
- `key` (str): Ciąg binarny reprezentujący wielomian generujący (np. `"1001"` dla prostego przypadku lub 33-bitowy dla CRC-32).

###### Zwraca
- `str`: Słowo kodowe (dane + CRC) jako ciąg binarny.

###### Wyjątki
- `ValueError`: Jeśli klucz jest pusty.

###### Przykład

```python
>>> CRC_visual("1000101", "101")
# Wyświetla kroki dzielenia binarnego i zwraca np.:
'100010101'
```

###### Kluczowe linie kodu

```python
dividend = code << (n - 1)
```

- Przesuwa dane w lewo o $ n-1 $ bitów, dopełniając je zerami, aby zarezerwować miejsce na sumę kontrolną.

```python
portion = dividend >> current_shft
```

- Pobiera $ n $ najbardziej znaczących bitów z dywidendy do operacji XOR.

```python
rem = portion ^ gen
```

- Wykonuje operację XOR między fragmentem danych a wielomianem generującym, realizując dzielenie w ciele GF(2).

```python
dividend = (dividend & ((1 << current_shft) - 1)) | (rem << current_shft)
```

- Symuluje dzielenie w słupku:
  - `(1 << current_shft) - 1`: Tworzy maskę bitową z jedynkami do pozycji `current_shft`.
  - `dividend & mask`: Usuwa $ n $-bitowy fragment z przodu dywidendy.
  - `rem << current_shft`: Wstawia wynik XOR na miejsce usuniętego fragmentu.

```python
toBin(dividend).zfill(total_bits)
```

- Zapewnia stałą długość ciągu binarnego w wizualizacji, dodając zera wiodące.

###### Wizualizacja
Funkcja wyświetla każdy krok dzielenia binarnego, podświetlając aktualnie przetwarzane bity (za pomocą kodów ANSI) oraz pokazując operacje XOR i przesunięcia.

---

##### check_crc(codeword, key)
Sprawdza poprawność słowa kodowego (dane + CRC) przez ponowne dzielenie binarne przez wielomian generujący.

###### Parametry
- `codeword` (str): Słowo kodowe (dane + CRC) jako ciąg binarny.
- `key` (str): Wielomian generujący jako ciąg binarny.

###### Zwraca
- Brak. Funkcja wyświetla:
  - Resztę z dzielenia (jeśli `0`, brak błędów).
  - Komunikat o powodzeniu lub niepowodzeniu weryfikacji CRC.

###### Przykład

```python
>>> check_crc("100010101", "101")
# Wyświetla:
Reszta po sprawdzeniu: 0
✅ CRC check passed: brak błędów.
```

###### Kluczowe linie kodu

```python
current_shft = dividend.bit_length() - n
```

- Określa, czy dywidenda ma wystarczającą liczbę bitów do kolejnej operacji XOR.

```python
rem = (dividend >> current_shft) ^ gen
```

- Pobiera fragment dywidendy i wykonuje XOR z wielomianem generującym.

```python
dividend = (dividend & ((1 << current_shft) - 1)) | (rem << current_shft)
```

- Aktualizuje dywidendę po każdej iteracji, podobnie jak w `CRC_visual`.

```python
if dividend == 0:
    print("✅ CRC check passed: brak błędów.")
else:
    print("❌ CRC check failed: wykryto błąd.")
```

- Sprawdza, czy reszta wynosi `0` (brak błędów) i wyświetla odpowiedni komunikat.

---

### 4.2 Kod źródłowy
Poniżej znajduje się pełny kod źródłowy programu w Pythonie, który wizualizuje proces obliczania CRC-32 oraz weryfikacji sumy kontrolnej.

```python
def toBin(num):
    return bin(num)[2:] if num != 0 else "0"


def toDec(bin_str):
    return int(bin_str, 2) if bin_str else 0


def CRC_visual(data, key):
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
    data = "111010001100101011100110111010010001110100011110010100011010"
    generator_hex = "0x04C11DB7"
    generator_bin = bin(int(generator_hex, 16))[2:].zfill(32)
    generator_bin = "1" + generator_bin  # upewniamy się, że jest 33-bitowy

    """Do testow"""
    # data = "1000101"
    # generator_bin = "101"

    print("-" * 10 + " CRC wizualizacja z 802.3/802.11 polynomem " + "-" * 10)
    print(f"Generator G(x): {generator_bin}")
    print("-" * 60)

    codeword = CRC_visual(data, generator_bin)
    check_crc(codeword, generator_bin)
```

---

### 4.3. Omówienie kodu

Kod składa się z czterech głównych funkcji:
1. **`toBin(num)`**: Konwertuje liczbę dziesiętną na ciąg binarny, usuwając prefiks `0b`. Zwraca `"0"` dla zera.
2. **`toDec(bin_str)`**: Konwertuje ciąg binarny na liczbę dziesiętną.
3. **`CRC_visual(data, key)`**: Implementuje algorytm CRC-32 z wizualizacją krok po kroku:
   - Przyjmuje dane wejściowe i wielomian generujący jako ciągi binarne.
   - Dopełnia dane zerami (przesunięcie bitowe w lewo o $ n-1 $).
   - Wykonuje dzielenie binarne z operacjami XOR.
   - Wyświetla kolejne kroki dzielenia, podświetlając aktualnie przetwarzane bity.
   - Zwraca słowo kodowe (dane + CRC).
4. **`check_crc(codeword, key)`**: Weryfikuje poprawność słowa kodowego przez ponowne dzielenie. Jeśli reszta wynosi 0, dane są poprawne.

Program używa wielomianu generującego CRC-32 w formacie zgodnym z IEEE 802.3 (`0x04C11DB7` w postaci heksadecymalnej, z dołączonym bitem $ x^{32} $).

### 4.3. Wyniki uruchomienia

Przykładowe dane wejściowe:
- Dane: `00111010001100101011100110111010010001110100011110010100011010`
- Wielomian generujący: `100000100110000010001110110110111` (33 bity)

**Wynik działania funkcji `CRC_visual`:**

```python
---------- CRC wizualizacja z 802.3/802.11 polynomem ----------
Generator G(x): 100000100110000010001110110110111
------------------------------------------------------------
🔍 Wizualizacja obliczania CRC:

Wejściowe dane:    00111010001100101011100110111010010001110100011110010100011010
Generator (key):   100000100110000010001110110110111
Dane + zera:       0011101000110010101110011011101001000111010001111001010001101000000000000000000000000000000000
Rozpoczynam dzielenie binarne...

Divident bits : 0011101000110010101110011011101001000111010001111001010001101000000000000000000000000000000000
  XORing:       111010001100101011100110111010010
          XOR   100000100110000010001110110110111
        =       011010101010101001101000001100101
Posuwam się dalej w prawo (shift = 59)

Divident bits : 0001101010101010100110100000110010100111010001111001010001101000000000000000000000000000000000
  XORing:       110101010101010011010000011001010
          XOR   100000100110000010001110110110111
        =       010101110011010001011110101111101
Posuwam się dalej w prawo (shift = 58)

Divident bits : 0000101011100110100010111101011111010111010001111001010001101000000000000000000000000000000000
  XORing:       101011100110100010111101011111010
          XOR   100000100110000010001110110110111
        =       001011000000100000110011101001101
Posuwam się dalej w prawo (shift = 57)

Divident bits : 0000001011000000100000110011101001101111010001111001010001101000000000000000000000000000000000
  XORing:       101100000010000011001110100110111
          XOR   100000100110000010001110110110111
        =       001100100100000001000000010000000
Posuwam się dalej w prawo (shift = 55)

Divident bits : 0000000011001001000000010000000100000001010001111001010001101000000000000000000000000000000000
  XORing:       110010010000000100000001000000010
          XOR   100000100110000010001110110110111
        =       010010110110000110001111110110101
Posuwam się dalej w prawo (shift = 53)

Divident bits : 0000000001001011011000011000111111011010110001111001010001101000000000000000000000000000000000
  XORing:       100101101100001100011111101101011
          XOR   100000100110000010001110110110111
        =       000101001010001110010001011011100
Posuwam się dalej w prawo (shift = 52)

Divident bits : 0000000000001010010100011100100010110111000001111001010001101000000000000000000000000000000000
  XORing:       101001010001110010001011011100000
          XOR   100000100110000010001110110110111
        =       001001110111110000000101101010111
Posuwam się dalej w prawo (shift = 49)

Divident bits : 0000000000000010011101111100000001011010101111111001010001101000000000000000000000000000000000
  XORing:       100111011111000000010110101011111
          XOR   100000100110000010001110110110111
        =       000111111001000010011000011101000
Posuwam się dalej w prawo (shift = 47)

Divident bits : 0000000000000000011111100100001001100001110100011001010001101000000000000000000000000000000000
  XORing:       111111001000010011000011101000110
          XOR   100000100110000010001110110110111
        =       011111101110010001001101011110001
Posuwam się dalej w prawo (shift = 44)

Divident bits : 0000000000000000001111110111001000100110101111000101010001101000000000000000000000000000000000
  XORing:       111111011100100010011010111100010
          XOR   100000100110000010001110110110111
        =       011111111010100000010100001010101
Posuwam się dalej w prawo (shift = 43)

Divident bits : 0000000000000000000111111110101000000101000010101011010001101000000000000000000000000000000000
  XORing:       111111110101000000101000010101011
          XOR   100000100110000010001110110110111
        =       011111010011000010100110100011100
Posuwam się dalej w prawo (shift = 42)

Divident bits : 0000000000000000000011111010011000010100110100011100010001101000000000000000000000000000000000
  XORing:       111110100110000101001101000111000
          XOR   100000100110000010001110110110111
        =       011110000000000111000011110001111
Posuwam się dalej w prawo (shift = 41)

Divident bits : 0000000000000000000001111000000000011100001111000111110001101000000000000000000000000000000000
  XORing:       111100000000001110000111100011111
          XOR   100000100110000010001110110110111
        =       011100100110001100001001010101000
Posuwam się dalej w prawo (shift = 40)

Divident bits : 0000000000000000000000111001001100011000010010101010000001101000000000000000000000000000000000
  XORing:       111001001100011000010010101010000
          XOR   100000100110000010001110110110111
        =       011001101010011010011100011100111
Posuwam się dalej w prawo (shift = 39)

Divident bits : 0000000000000000000000011001101010011010011100011100111001101000000000000000000000000000000000
  XORing:       110011010100110100111000111001110
          XOR   100000100110000010001110110110111
        =       010011110010110110110110001111001
Posuwam się dalej w prawo (shift = 38)

Divident bits : 0000000000000000000000001001111001011011011011000111100101101000000000000000000000000000000000
  XORing:       100111100101101101101100011110010
          XOR   100000100110000010001110110110111
        =       000111000011101111100010101000101
Posuwam się dalej w prawo (shift = 37)

Divident bits : 0000000000000000000000000001110000111011111000101010001011101000000000000000000000000000000000
  XORing:       111000011101111100010101000101110
          XOR   100000100110000010001110110110111
        =       011000111011111110011011110011001
Posuwam się dalej w prawo (shift = 34)

Divident bits : 0000000000000000000000000000110001110111111100110111100110011000000000000000000000000000000000
  XORing:       110001110111111100110111100110011
          XOR   100000100110000010001110110110111
        =       010001010001111110111001010000100
Posuwam się dalej w prawo (shift = 33)

Divident bits : 0000000000000000000000000000010001010001111110111001010000100000000000000000000000000000000000
  XORing:       100010100011111101110010100001000
          XOR   100000100110000010001110110110111
        =       000010000101111111111100010111111
Posuwam się dalej w prawo (shift = 32)

Divident bits : 0000000000000000000000000000000001000010111111111110001011111100000000000000000000000000000000
  XORing:       100001011111111111000101111110000
          XOR   100000100110000010001110110110111
        =       000001111001111101001011001000111
Posuwam się dalej w prawo (shift = 28)

Divident bits : 0000000000000000000000000000000000000011110011111010010110010001110000000000000000000000000000
  XORing:       111100111110100101100100011100000
          XOR   100000100110000010001110110110111
        =       011100011000100111101010101010111
Posuwam się dalej w prawo (shift = 23)

Divident bits : 0000000000000000000000000000000000000001110001100010011110101010101011100000000000000000000000
  XORing:       111000110001001111010101010101110
          XOR   100000100110000010001110110110111
        =       011000010111001101011011100011001
Posuwam się dalej w prawo (shift = 22)

Divident bits : 0000000000000000000000000000000000000000110000101110011010110111000110010000000000000000000000
  XORing:       110000101110011010110111000110010
          XOR   100000100110000010001110110110111
        =       010000001000011000111001110000101
Posuwam się dalej w prawo (shift = 21)

Divident bits : 0000000000000000000000000000000000000000010000001000011000111001110000101000000000000000000000
  XORing:       100000010000110001110011100001010
          XOR   100000100110000010001110110110111
        =       000000110110110011111101010111101
Posuwam się dalej w prawo (shift = 20)

Divident bits : 0000000000000000000000000000000000000000000000011011011001111110101011110100000000000000000000
  XORing:       110110110011111101010111101000000
          XOR   100000100110000010001110110110111
        =       010110010101111111011001011110111
Posuwam się dalej w prawo (shift = 14)

Divident bits : 0000000000000000000000000000000000000000000000001011001010111111101100101111011100000000000000
  XORing:       101100101011111110110010111101110
          XOR   100000100110000010001110110110111
        =       001100001101111100111100001011001
Posuwam się dalej w prawo (shift = 13)

Divident bits : 0000000000000000000000000000000000000000000000000011000011011111001111000010110010000000000000
  XORing:       110000110111110011110000101100100
          XOR   100000100110000010001110110110111
        =       010000010001110001111110011010011
Posuwam się dalej w prawo (shift = 11)

Divident bits : 0000000000000000000000000000000000000000000000000001000001000111000111111001101001100000000000
  XORing:       100000100011100011111100110100110
          XOR   100000100110000010001110110110111
        =       000000000101100001110010000010001
Posuwam się dalej w prawo (shift = 10)

Divident bits : 0000000000000000000000000000000000000000000000000000000000001011000011100100000100010000000000
  XORing:       101100001110010000010001000000000
          XOR   100000100110000010001110110110111
        =       001100101000010010011111110110111
Posuwam się dalej w prawo (shift = 1)

🔚 Koniec dzielenia.
🔸 Reszta (CRC):     11001010000100100111111101101110
🔸 Codeword (dane + CRC): 0011101000110010101110011011101001000111010001111001010001101011001010000100100111111101101110

🔍 Sprawdzanie poprawności odebranego kodu...

Reszta po sprawdzeniu: 0
✅ CRC check passed: brak błędów.
```

Wyniki potwierdzają poprawność implementacji – reszta z dzielenia słowa kodowego wynosi 0, co oznacza brak błędów.

### 4.4. Testy z błędami

Aby zweryfikować zdolność wykrywania błędów, zmodyfikowano słowo kodowe przez zmianę ostatniego bitu w reszcie. Wynik:

```python
---------- CRC wizualizacja z 802.3/802.11 polynomem ----------
Generator G(x): 100000100110000010001110110110111
------------------------------------------------------------
🔍 Sprawdzanie poprawności odebranego kodu...

Reszta po sprawdzeniu: 1
❌ CRC check failed: wykryto błąd.
```

Testy potwierdzają, że CRC-32 skutecznie wykrywa błędy pojedynczego bitu, zgodnie z teoretycznymi założeniami.

---

## 5. Implementacja sprzętowa w MultiSim


[[Multisim_video]](https://www.youtube.com/watch?v=yPu_bk8WcsA)

---

## 6. Literatura
- [1] [Cyclic_redundancy_check_wikipedia](https://en.wikipedia.org/wiki/Cyclic_redundancy_check)
- [2] [Mathematics_of_CRC](https://en.wikipedia.org/wiki/Mathematics_of_cyclic_redundancy_checks)
- [3] [IEEE 802.3 - 2022](https://ieeexplore.ieee.org/document/9844436)