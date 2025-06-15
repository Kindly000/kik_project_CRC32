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

Wiadomości są reprezentowane jako wielomiany \( M(x) \), gdzie każdy bit odpowiada współczynnikowi. Na przykład ciąg bitów `1011` odpowiada wielomianowi \( x^3 + x + 1 \).

#### Wielomian generujący
Standardowy wielomian generujący dla CRC-32 (IEEE 802.3) to:
\[ G(x) = x^{32} + x^{26} + x^{23} + x^{22} + x^{16} + x^{12} + x^{11} + x^{10} + x^8 + x^7 + x^5 + x^4 + x^2 + x + 1 \]
W postaci binarnej: `100000100110000010001110110110111` (33 bity, w tym bit najwyższego stopnia).

#### Proces obliczania CRC
1. **Dopełnienie danych**: Dane wejściowe są mnożone przez \( x^{32} \), co odpowiada dopełnieniu 32 zerami na końcu.
\[ M'(x) = M(x) \cdot x^{32}\]
2. **Dzielenie wielomianowe**: Dopełnione dane są dzielone przez \( G(x) \) w ciele GF(2). Reszta z dzielenia (32 bity) stanowi sumę kontrolną CRC.
\[ M'(x) = Q(x) \cdot G(x) + R(x) ,\; deg(R(x)) < 32 \]
3. **Dołączanie sumy kontrolnej**: Reszta \( R(x) \) jest dołączana do oryginalnych danych, tworząc słowo kodowe.
4. **Weryfikacja**: Odbiorca dzieli otrzymane słowo \( M'(x) \) kodowe przez \( G(x) \). Jeśli reszta wynosi 0, dane są poprawne.
\[ M'(x)\;mod\;G(x) = 0\]

#### Projektowanie wielomianu generującego
Wielomian \( G(x) \) musi być starannie wybrany, aby zapewnić wysoką skuteczność wykrywania błędów. Kluczowe cechy:
- **Wielomian pierwotny**: ma on największy "cykl" wykrywalności. Wykrywa: wszystkie 1-bitowe błędy, wszystkie 2-bitowe błędy jeśli blok_danych $\le 2^{r} - 1$, gdzie `r` to stopień wielomianu.
Nie mamy natomiast gwarancji wykrycia wszystkich błędów 3-bitowych, 4-bitowych itd. 
- **Wielomian typu \( g(x) = p(x) \cdot (x+1) \)** , \(p(x) \to \) pierwiastek pierwotny stopnia `(r-1)`: Wykrywa wszystki błędy 1-bitowe, 2-bitowe oraz wszystkie błędy o nieparzystej liczbie błędów.
Ma on natomiast krótszy maksymalny blok danych, w którym można wykryć błąd: \( 2^{r-1} - 1\), czyli o połowe mniej niż w przypadku pierwotnego wielomianu generującego.
- **Wielomiany rozkładalne**: Wielomian jest rozkładalny, jeśli da się go zapisać w następujący sposób:
\[ g(x) = f(x) \cdot h(x)\]
W takiej sytuacji pierścień resztkowy nie jest ciałem, tylko ma w sobie tzw. zero-dzielniki. Są to takie elementy \(a(x)\), dla których istnieje element niezerowy \(b(x)\), taki że:
\[a(x) \cdot b(x) = 0 \; mod \; g(x)\]
Jeżeli jakikolwiek błąd przyjmie taką właśnie postać, to nie będziemy w stanie go wykryć za pomocą CRC. 
#### Możliwości detekcyjne CRC
CRC-32 jest w stanie wykryć:
- **Błędy pojedynczego bitu**: Zawsze, jeśli \( G(x) \) ma co najmniej dwa niezerowe wyrazy.
- **Błędy dwóch bitów**: Jeśli odległość między błędnymi bitami jest mniejsza niż rząd wielomianu pierwotnego.
- **Błędy o nieparzystej liczbie bitów**: Jeśli \( G(x) \) jest podzielny przez \( (x+1) \).
- **Błędy burst**: Ciągłe sekwencje błędnych bitów o długości mniejszej niż stopień \( G(x) \), jeśli najwyższy współczynnik i wyraz wolny są niezerowe.
- **Wszystkie kombinacje błędów mniejszych niż minimalna odległość Hamminga**: Dla CRC-32 minimalna odległość Hamminga wynosi co najmniej 4, co oznacza wykrywanie wszystkich błędów 1-, 2- i 3-bitowych.

Problemy z wykrywaniem:
- Błędy na początku sekwencji (zera na początku).
- Błędy o parzystej liczbie bitów, jeśli \( G(x) \) nie zawiera \( (x+1) \).

---

## 3. Algorytm CRC-32

Algorytm CRC-32 według standardu IEEE 802.3 (zdefiniowany m.in. w IEEE 802.11 z 1997 r.) polega na:
1. Przyjęciu danych wejściowych jako ciągu bitów.
2. Dopełnieniu danych 32 zerami.
3. Wykonaniu dzielenia wielomianowego przez wielomian generujący.
4. Dołączeniu 32-bitowej reszty jako sumy kontrolnej.
5. Weryfikacji po stronie odbiorcy przez powtórzenie dzielenia.

---

## 4. Implementacja w Pythonie

### 4.1. Dokumentacja kodu

Poniżej przedstawiono kod źródłowy programu w Pythonie, który wizualizuje proces obliczania CRC-32 oraz weryfikacji sumy kontrolnej.

<xaiArtifact artifact_id="7d04a858-3649-4c0b-a7f7-e324bb8c26e0" artifact_version_id="25e8f384-a5c3-46f0-af92-f244d9aef7e6" title="crc32binarydemo.py" contentType="text/python">
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
    dividend = code << (n - 1)
    total_bits = data_len + n - 1
    print(f"Wejściowe dane:    {data}")
    print(f"Generator (key):   {key}")
    print(f"Dane + zera:       {toBin(dividend).zfill(total_bits)}")
    print(f"Rozpoczynam dzielenie binarne...\n")
    while True:
        current_shft = dividend.bit_length() - n
        if current_shft > max_shift:
            max_shift = current_shft
        if current_shft < 0:
            break
        portion = dividend >> current_shft
        portion_bin = toBin(portion).zfill(n)
        gen_bin = toBin(gen).zfill(n)
        rem = portion ^ gen
        rem_bin = toBin(rem).zfill(n)
        dividend_bin = toBin(dividend).zfill(total_bits)
        start_idx = total_bits - dividend.bit_length()
        portion_start = start_idx
        portion_end = portion_start + n
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
        dividend = (dividend & ((1 << current_shft) - 1)) | (rem << current_shft)
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
    generator_bin = "1" + generator_bin
    print("-" * 10 + " CRC wizualizacja z 802.3/802.11 polynomem " + "-" * 10)
    print(f"Generator G(x): {generator_bin}")
    print("-" * 60)
    codeword = CRC_visual(data, generator_bin)
    check_crc(codeword, generator_bin)