Badita Rares

DESCRIERE SCURTA:
Program python ce ia ca input o expresie regulata si o transforma intr-un automat deterministic finit.
Expresia regulata poate contine doar paranteze, Kleen Star si reuniune. Restul caracterelor sunt tratate drept simboli ai alfabetului. Concatenarea este implicita (nu necesita caracter).

MODUL DE RULARE A PROGRAMULUI:
python3 main.py [in file] [nfa out file] [dfa out file] ['T' pentru afisarea grafurilor | optional] ['T' pentru simplificarea tree-ului | optional]

DESCRIERE IN AMANUNT:
A. Transformarea din regex in NFA
Transformarea cuprinde 3 pasi:
1)   Crearea unei liste de noduri
2.1) Aranjarea nodurilor intr-un arbore apropae-binar
2.2) Simplificarea arborelui binar (optional)
3)   Crearea NFA din arbore 

Functia ce transforma sirul de caractere in arbore (parse) se regaseste in exprAnalysis si cuprinde in cadrul ei
alte functii ce se ocupa separat de pasii 1, 2.1, 2.2
Functia pentru pasul 3 se refaseste in clasa NFA (fisierul automaton)

Voi merge mai departe prin a demonstra exemplul aba|c*

1) Crearea listei de noduri: (pas de preprocesre)
Se pracurge sirul dat si se formeaza o lista de noduri ce contin 2 atribute (tokentype si value)
	- tokentype este o valoare ce salveaza tipul operatorului (paranteza, litera, concatenare etc.)
	  clasa TokenType din exprAnalysis contine valorile pentru acestea
	- value este valoare propriuzisa a caraterului din sir
Functia adauga concatenare (tokentype = TokenType.T_CON) intre:
	- o paranteza inchisa si o litera/o paranteza deschisa
	- un Kleene star si o litera/paranteza deschisa
	- o litera si o paranteza deschisa/ o alta litera
De asemenea, functia la intalnirea caracterului '|' in sir adauga 3 noduri (<)>; <|>; <(>) in lista
Rezultatului i se adauga o paranteza deschisa la incepul si una inchisa la sfarsit
Aceasta este pentru a asigura cel mai mic nivel de precedenta operatiei de reuniune, fara a schimba structura sirului

Rezultatul pentru regexul de mai sus este [<(> <a> <+> <b> <+> <a> <)> <|> <(> <c> <*> <)>]

2) Crearea arborelui:
Intr-un prim pas, functia parcurge odata lista de caractere si formeaza un arbore aprope-binar bazat pe aceasta
Prin aproape-binar inteleg ca operatiile de concatenare si reuniune din arbore vor avea 2 copii exact, insa operatia Kleene star are doar un copil

Functia este una ce parcurge lista de noduri, facand pop din aceasta la fiecare iteratie, pana cand lista este vida
Functia asigneaza un nod drept head al arborelui si intoarce drept rezultat acest head
La fiecare nod '(', se reapeleaza functia cu resul de lista de noduri ramase, rezultatul fiind adaugat frept copil al nodului curent marcat drept head
La intalnirea nodurilor ')', se intoarece headul curent drept rezultat al subrutinei
La intalnirea nudurilor '+' sau '|', acesta devine noul head, iar vechiul head devine copilul acestuia
La inalnirea unei litere, aceasta doar devine copilul headului actual
Pentru a asigura precedenta maxima operatiei Kleene star, aparitea acesteia in sirul de noduri se face imediat dupa citirea unui nod litera sau ')'

Datorita pasului anterior de preprocesare si a verificarii Kleene star-ului in avans, asiguram o precedenta a operatorilor * > + > |

Rezultatul calcului de mai sus pentru regexul "aba|c*" ar fi arborele din stanga, care poate fi simplificat prin eliminarea concatenarii intermediare:

		  |					  |
		 / \				 / \
		+	*				+   *
	   / \	 \			   /|\   \
	  +  a    c   =>	  a b a   c
	 / \
	a  b

Simplificarea arborelui se refera la transformarea acestuia din unul binar in unul cu numar nedefinit de copii, pentru a reduce numarul de noduri si adancimea acestuia
Arborele este parcurs intr-un DFS root-left-right. Odata ce nodul curent iese din bucla de dfs, se mai cicleaza odata prin copii acestuia:
	- daca copilul are acelasi TokenType ca nodul curent, atunci nodul curent ii mosteneste direct copii acestuia
	- daca copilul nu are acelasi TokenType, atunci contunua sa il mosteneasca pe acesta

Pasul de simplificare se executa doar daca al 5-lea parametru a fost setat la valoarea de True.

3) Transformarea din arbore in NFA: (functia statica convert)
Arborele este parcurs intr-un DFS root-left-right (functia accept)
NFA-ul incepe cu starea 0 (desemnata drept stare de start implicit)
Pe parcursul algoritmului numarul de stari din NFA este utilizat drept punct de plecare pentru acceptarea urmatorului nod din arbore
Practic in urma acceptari unei ramuri din arbore s-au creeat x stari, iar starea x-1 poate fi folosita ca punct de plecare pentru acceptarea urmatoarei ramuri

In functie de tipul nodului, se apeleaza o functie specifica a sa ce adauga in NFA stari si tranzitii necesare pentru acceptarea acestuia

La final se desemneaza ultima stare drept stare finala

stare initiala:					[0]

acceptare a 3 concatenari:		[0]        [1] -a- > [2] -b- > [3] -a-> [4]

conexiunea copil 1 al |:		[0] -eps-> [1] -a- > [2] -b- > [3] -a-> [4]

acceptul c*:					[0] -eps-> [1] -a- > [2] -b- > [3] -a-> [4]
										   [5] -eps-> [6] -c-> [7] -eps-> [8]
											|          ^--eps---|		   ^
											--------------eps--------------|

conexiune copil 2 al |:			[0] -eps-> [1] -a- > [2] -b- > [3] -a-> [4]
								 |---eps-->[5] -eps-> [6] -c-> [7] -eps-> [8]
											|          ^--eps---|		   ^
											--------------eps--------------|

final:							[0] -eps-> [1] -a- > [2] -b- > [3] -a-> [4] ---eps----> [9]
								 |---eps-->[5] -eps-> [6] -c-> [7] -eps-> [8] -eps-------^
											|          ^--eps---|		   ^
											--------------eps--------------|

B. Transformarea din NFA in DFA
Procesul de transformare din DFA in NFA se bazeaza pe un algoritm de baza. O explicatie a acestuia se poate regasi pe internet.
Programul doar reproduce acel algoritm.