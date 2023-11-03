# Informatique Fondamentale Projet

## Variables

- $p_n$: si l'état $n$ est dans l'automate
- $a_{n}$: si l'état $n$ est acceptant
- $t_{i,j,l}$ si il y a une transition de l'état $i$ à $j$ avec la lettre $l$
- $v_{n,x,w}$ si l'état $n$ est visité à la position $x$ du mot $w$

## Contraintes

1.  La source est dans l'automate.  
	$p_{0}$

2. Il y a au moins un état acceptant dans l'automate.  
	$\bigvee\limits_{n=0}^{k} a_{n}$

3. Tous les états acceptants font partie de l'automate.  
	$\bigwedge\limits_{n=0}^{k}a_{n}\rightarrow p_{n} \quad$ mise en FNC $\quad \bigwedge\limits_{n=0}^{k} \lnot a_{n} \lor p_{n}$

4. Toutes les transitions sont valides.  
	$\bigwedge\limits_{i=0}^{k}\bigwedge\limits_{j=0}^{k}\bigwedge\limits_{l\in\Sigma} t_{i,j,l} \rightarrow p_{i} \land p_{j}$  
	
	$\bigwedge\limits_{i=0}^{k}\bigwedge\limits_{j=0}^{k}\bigwedge\limits_{l\in\Sigma} \lnot t_{i,j,l} \lor (p_{i} \land p_{j})$  
	
	$\bigwedge\limits_{i=0}^{k}\bigwedge\limits_{j=0}^{k}\bigwedge\limits_{l\in\Sigma} (\lnot t_{i,j,l} \lor p_{i}) \land (\lnot t_{i,j,l} \lor p_{j})$  

5. L'automate est consistant.  
	1.  Toutes les exécutions commencent à la source.  
		$\bigwedge\limits_{w\in P \cup N} v_{0,0, w}$  

	2. Toutes les exécutions des mots de $P$ sont acceptantes.  
		$\bigwedge\limits_{w \in P}\bigwedge\limits_{n=0}^{k} v_{n, L(w), w} \rightarrow a_{n} \quad$ mise en FNC $\quad \bigwedge\limits_{w \in P}\bigwedge\limits_{n=0}^{k} \lnot v_{n, L(w), w} \lor a_{n}$  

	3. Toutes les exécutions des mots de $P$ sont acceptantes.  
		$\bigwedge\limits_{w \in N}\bigwedge\limits_{n=0}^{k} v_{n, L(w), w} \rightarrow \lnot a_{n} \quad$ mise en FNC $\quad \bigwedge\limits_{w \in N}\bigwedge\limits_{n=0}^{k} \lnot v_{n, L(w), w} \lor \lnot a_{n}$

	4. Les exécutions.  
		$\bigwedge\limits_{w\in P \cup N} \bigwedge\limits_{x=0}^{L(w)-1}\bigwedge\limits_{i=0}^{k} v_{i,x,w} \rightarrow \bigwedge\limits_{j=0}^{k} t_{i,j,w[x]} \rightarrow v_{j,x+1,w}$
		
		$\bigwedge\limits_{w\in P \cup N} \bigwedge\limits_{x=0}^{L(w)-1}\bigwedge\limits_{i=0}^{k} \lnot v_{i,x,w} \lor \bigwedge\limits_{j=0}^{k} \lnot t_{i,j,w[x]} \lor v_{j,x+1,w}$
		
		$\bigwedge\limits_{w\in P \cup N} \bigwedge\limits_{x=0}^{L(w)-1}\bigwedge\limits_{i=0}^{k} \bigwedge\limits_{j=0}^{k} \lnot v_{i,x,w} \lor \lnot t_{i,j,w[x]} \lor v_{j,x+1,w}$

