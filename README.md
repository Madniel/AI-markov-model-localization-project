# Lokalizacja - Raport

Poniżej znajduje się raport opisujący działanie programu. Raport został podzielony na dwie częsci: Obliczanie rozkładu lokalizacji robota i Heurystykę

##Obliczanie rozkładu lokalizacji robota

Do obliczenia rozkładu lokalizacji robota wykorzystywane są trzy macierze:

T - macierz przejścia 

O - macierz zawierająca pomiary z sensora

P - macierz rozkładu położenia robota

Cały proces jest oparty o aktualizowanie macierzy P za pomoca mnożenia jej przez czynnik przejścia a potem macierz O

##Macierz P

Macierz P składa się z 42 wektorów po 4 wartości. Wektory reprezentują wolne miejsca (których jest 42), a wartości poszczególne orientacje. 
Początkowo wszystkie lokacje posiadają jednakowe prawdopodobieństwo równe 1/42 * 1/4. 

##Macierz T

Macierz T ma rozmiar 42x42x4x4. Jest to związane, z tym, że dla czterech orientacji pod uwagę trzeba wziąć wszystkie mozliwe sytuacje. 
Orientacje w wektorze umiejscawiane są zgodnie z kolejnością ['N','E','S','W']

Jeśli w zbiorze percept wykryto wykryto "bump" (robot uderzył w ściane) to dla każdej lokacji tworzona jest macierz jednostkowa,
ponieważ robot na 100% (czyli 1.0) zostanie w danym miejscu w danej orientacji.

W przypadku skrętu w prawo w wektorze w miejsce danego kierunku wpisujemy 0.05 a dla kierunku po prawej 0.95 
np. dla orientacji N wynosi --> [0.05, 0.95 ,0 ,0], a dla S --> [0 ,0,0.05, 0.95]. 

W podobny sposób robimy w przypadku skrętu w lewo. Zmieniamy tylko miejsca dla wartości (zamiast [0 ,0,0.05, 0.95] na [0 ,0.95,0.05,0]).

Dla ruchu do przodu do każdej lokacji tworzona jest lista lokacji sąsiadujących. Następnie sprawdzane jest czy sąsiedzi są ścianą.
Jesli dany sąsiad nie jest ścianą to dla każdej lokacji tworzona jest macierz równa macierzy jednostkowej przemnożonej razy 0.05.
Wynika to z tego, że  istnieje 0.05 prawdopodobienstwa, że robot zostanie na danym miejscu w danej orientacji.
Następnie dla kolejnej lokacji tworzona jest macierz równa macierzy jednostkowej przemnożonej razy 0.95.
Wynika to z tego, że  istnieje 0.95 prawdopodobienstwa, że robot przeniesie się na dane miejsce w niezmiennej orientacji.
Tak dla każdego miejsca powstaje macierz 4x4
Jeśli sąsiad jest ścianą to na miejsce orientacji w danym wektorze wpisywana jest wartość 1.

##Macierz 0

Macierz O ma rozmiar 42x4. Dla każdego położenia jest tworzony wektor 4 elementowy.
Każdy element w tym wektorze określa prawdopodobieństwo dla poszczególnej orientacji robota.
Tworzone jest pięć list. Pierwsze cztery to listy dla poszczególnych przypadków położenia robota. Sąsiedzi danej lokacji są w nich umiejscawiani w innych kolejnosciach 
([N,E,S,W], [E,S,W,N], [S,W,N,E], [W,N,E,S])

Piąta lista natomiast to zbiór wszystkich tych list.
Pętla for sprawdza każdą orientacje i jeśli sensor poprawnie określił położenie ścian to mnoży zmienną tymaczasową "a" 
(z wartością początkową 1.0) razy 0.9,a jeśli źle to 0.1.
Jeśli wystąpi 'bump' w 'percept' to wówczas dla orientacji 'fwd' mnoży się zmienną 'a' razy 1.0. 

Cykl ten jest powtarzany dla wszystkich list i wyniki (wartości zmiennej 'a') zapisywane są w wektorze. 

Powtarzane jest to dla wszystkich lokacji więc otrzymujemy macierz 42x4.

##Mnożenie macierzy

Na samym początku wykonujemy mnożenie macierzy T i P. 

Macierz T transponujemy, ponieważ wiersze muszą odpowiadać następnym stanom. W oryginalny T wiersze odpowiadają obecnym stanom.

Mnożenie T i P polega na mnożeniu macierzowym kolejnych macierzy danego stanu przez kolejne wiersze macierzy P.
Wynikowe wektory są dodawane do siebie i zapisywane jak wektor macierzy P dla danego stanu

Następnie każdy element macierzy P jest przemnażany przez każdy element macierzy O.

Na samym końcu normalizujemy macierz P tak, by suma elementów w macierzy wynosiła łącznie 1.

##Heurystyka

Heurystyka jest oparta na zasadzie poruszania się robotem jak najczęsściej do przodu.
W ten sposób robot najszybciej dokunuje zbieżności algorytmu i oblicza prawdopodobieństwo swego położenia i orientacji.

Heurystyka dzieli się na 3 podpunkty.

Na samym początku sprawdzane jest czy robot nie wpadł w ścianę. Jeśli nie występują ściany bądź ściany występują zarówno po lewej jak i prawej
wówczas robot losowo obraca się w lewo lub prawo (szansa na obrót w jedną ze stron wynosi 50% na 50%). Jeśli natomiast obok robota znajduje się jedna ściana
to robot obraca się przeciwnie do niej. 

Jeśli robot nie wpadł w ściane ,a przeszkoda zostanie wykryta z przodu to najpierw zostaje sprawdzone czy ściana występują  tylko po lewej lub po prawej stronie. 
Agent wbiera wtedy zwrot w przeciwną stronę. Jeśli ściany występują po bokach robota to zwrot określany jest na podstawie poprzedniego ruchu. 
Jeśli był to skręt w lewo/prawo robot powtarza czynność. Jeśli nie, robot zmierza do przodu.

Jeśli z przodu nie ma ściany to obrót robota zależy od trzech cznników. 
Jeśli sensor wykrywa tylko jedną ściane, ma pozwolenie na obrót oraz poprzednim jego ruchem nie był obrót to może wykonać zwrot w lewo lub prawo.
Zależne jest to od tego po której stronie znajduje się ściana. Pozwolenie na ruch zostaje nadane wraz
inicjalizacją programu oraz w momencie ruchu robota do przodu. Jeśli robot wykona zwrot w któryms kierunku następuje odebranie pozwolenia aż do momentu ruchu do przodu.
Jeśli warunki zostaną spełnione wówczas ruch jest losowo wybierany z zbioru ['forward' , 'turnleft/turnroght'] z prawdopodobieństwem [0.6,0.4]. 
Umożliwia to robotowi wyjście z części korytarza w kształcie "T". Jednocześnie jednak wciaż kładzony jest nacisk na ruch do przodu.
Jeśli robot nie może wykonać ruchu w prawo/lewo następuje ruch do przodu.

# Localization-project
