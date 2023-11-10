# Informatique Fondamentale Projet
## Variables

- $p_n$: si l'état $n$ est dans l'automate
- $a_{n}$: si l'état $n$ est acceptant
- $t_{i,j,l}$ si il y a une transition de l'état $i$ à $j$ avec la lettre $l$
- $v_{n,x,w}$ si l'état $n$ est visité à la position $x$ du mot $w$

## Contraintes

### Construction

1.  La source est dans l'automate.  
	$p_{0}$

2. Tous les états acceptants font partie de l'automate.  
	$\bigwedge\limits_{n=0}^{k}a_{n}\rightarrow p_{n}$
	
	$\bigwedge\limits_{n=0}^{k} \lnot a_{n} \lor p_{n}$

3. Toutes les transitions sont valides.  
	$\bigwedge\limits_{i=0}^{k}\bigwedge\limits_{j=0}^{k}\bigwedge\limits_{l\in\Sigma} t_{i,j,l} \rightarrow p_{i} \land p_{j}$
	
	$\bigwedge\limits_{i=0}^{k}\bigwedge\limits_{j=0}^{k}\bigwedge\limits_{l\in\Sigma} \lnot t_{i,j,l} \lor (p_{i} \land p_{j})$
	
	$\bigwedge\limits_{i=0}^{k}\bigwedge\limits_{j=0}^{k}\bigwedge\limits_{l\in\Sigma} (\lnot t_{i,j,l} \lor p_{i}) \land (\lnot t_{i,j,l} \lor p_{j})$

### Consistance

1.  Toutes les exécutions commencent à la source.  
	$\bigwedge\limits_{w\in P \cup N} v_{0,0, w}$

2. Il existe une exécution acceptante pour tous les mots de $P$.  
	$\bigwedge\limits_{w \in P}\bigvee\limits_{n=0}^{k} v_{n, |w|, w} \land a_{n}$ 

3. Il n'existe pas d'exécution acceptante pour tous les mots de $N$.  
	$\bigwedge\limits_{w \in N} \lnot \bigvee\limits_{n=0}^{k} v_{n, |w|, w}  \land a_{n}$
		
	$\bigwedge\limits_{w \in N}\bigwedge\limits_{n=0}^{k} \lnot v_{n, |w|, w} \lor \lnot a_{n}$

4.  Il doit existé au moins une exécution pour chaque mot de $P$.  
	$\bigwedge\limits_{w\in P} \bigwedge\limits_{x=0}^{|w|}\bigvee\limits_{i=0}^{k} v_{i,x,w}$

5. Un état est visité s'il y a une transition qui va de l'état visité précédent avec la lettre actuelle vers cet état.  
	$\bigwedge\limits_{w\in P \cup N} \bigwedge\limits_{x=0}^{|w|-1}\bigwedge\limits_{i=0}^{k} v_{i,x,w} \rightarrow \bigwedge\limits_{j=0}^{k} v_{j,x+1,w} \leftrightarrow t_{i,j,w[x]}$
	
	$\bigwedge\limits_{w\in P \cup N} \bigwedge\limits_{x=0}^{|w|-1}\bigwedge\limits_{i=0}^{k} \lnot v_{i,x,w} \lor\bigwedge\limits_{j=0}^{k} (v_{j,x+1,w} \rightarrow t_{i,j,w[x]}) \land (\lnot t_{i,j,w[x]} \rightarrow v_{j,x+1,w})$
	
	$\bigwedge\limits_{w\in P \cup N} \bigwedge\limits_{x=0}^{|w|-1}\bigwedge\limits_{i=0}^{k} \lnot v_{i,x,w} \lor \bigwedge\limits_{j=0}^{k} (\lnot v_{j,x+1,w} \lor t_{i,j,w[x]}) \land (\lnot t_{i,j,w[x]} \lor v_{j,x+1,w})$
	
	$\bigwedge\limits_{w\in P \cup N} \bigwedge\limits_{x=0}^{|w|-1}\bigwedge\limits_{i=0}^{k} \bigwedge\limits_{j=0}^{k} (\lnot v_{i,x,w} \lor \lnot v_{j,x+1,w} \lor t_{i,j,w[x]}) \land (\lnot v_{i,x,w} \lor \lnot t_{i,j,w[x]} \lor v_{j,x+1,w})$

### Déterminisme

1. Les transitions sont unique.
	$\bigwedge\limits_{l\in \Sigma} \bigwedge\limits_{x=0}^{k}\bigwedge\limits_{y=0}^{k} t_{x,y,l} \rightarrow \lnot \bigvee\limits_{z=0, y\neq z}^{k} t_{x,z,l}$
	
	$\bigwedge\limits_{l\in \Sigma} \bigwedge\limits_{x=0}^{k}\bigwedge\limits_{y=0}^{k} \lnot t_{x,y,l} \lor \lnot \bigvee\limits_{z=0, y\neq z}^{k} t_{x,z,l}$
	
	$\bigwedge\limits_{l\in \Sigma} \bigwedge\limits_{x=0}^{k}\bigwedge\limits_{y=0}^{k} \lnot t_{x,y,l} \lor \bigwedge\limits_{z=0, y\neq z}^{k} \lnot t_{x,z,l}$
	
	$\bigwedge\limits_{l\in \Sigma} \bigwedge\limits_{x=0}^{k}\bigwedge\limits_{y=0}^{k} \bigwedge\limits_{z=0, y\neq z}^{k} \lnot t_{x,y,l} \lor \lnot t_{x,z,l}$

### Complétude

1.  Pour chaque état il dois existé une transition sortante pour chaque lettre de l'alphabet. *(la contrainte 1 est incluse dans celle ci.)*  
	$\bigwedge\limits_{l\in \Sigma}\bigwedge\limits_{i=0}^{k}\bigvee\limits_{j=0}^{k} t_{i,j,l}$

2. Pour chaque état il doit existé une transition entrante.  
	$\bigwedge\limits_{i=0}^{k}\bigvee\limits_{j=0}^{k}\bigvee\limits_{l\in \Sigma} t_{j,i,l}$

### Réversibilité

1. Un état ne peut être visité uniquement en partant d'un état et en utilisant une transition inversée. *(vient de la contrainte 5 dans la consistance)*  
	$\bigwedge\limits_{w\in P \cup N} \bigwedge\limits_{x=0}^{|w|-1}\bigwedge\limits_{i=0}^{k} \bigwedge\limits_{j=0}^{k} (\lnot v_{j,x,w} \lor \lnot v_{i,x+1,w} \lor t_{j,i,w[x]}) \land (\lnot v_{j,x,w} \lor \lnot t_{j,i,w[x]} \lor v_{i,x+1,w})$
