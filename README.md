# Informatique Fondamentale Projet
## Variables

- $p_x$ : si l'état $x$ est dans l'automate
- $a_{x}$ : si l'état $x$ est acceptant
- $t_{x,y,l}$ : si il y a une transition de l'état $x$ à $y$ avec la lettre $l$
- $v_{x,i,w}$ : si l'état $x$ est visité à la position $i$ du mot $w$
### Transformation de Tseitin
- $x_{x,s,w}$ 
- $y_{x,y,i,w}$

## Contraintes

### Construction

1.  La source est dans l'automate.  
	$p_{0}$

2. Tous les états acceptants font partie de l'automate.  
	$\bigwedge\limits_{x=0}^{k}a_{x}\rightarrow p_{x}$
	
	$\bigwedge\limits_{x=0}^{k} \lnot a_{x} \lor p_{x}$

3. Toutes les transitions sont valides.  
	$\bigwedge\limits_{x=0}^{k}\bigwedge\limits_{y=0}^{k}\bigwedge\limits_{l\in\Sigma} t_{x,y,l} \rightarrow p_{x} \land p_{y}$
	
	$\bigwedge\limits_{x=0}^{k}\bigwedge\limits_{y=0}^{k}\bigwedge\limits_{l\in\Sigma} \lnot t_{x,y,l} \lor (p_{x} \land p_{y})$
	
	$\bigwedge\limits_{x=0}^{k}\bigwedge\limits_{y=0}^{k}\bigwedge\limits_{l\in\Sigma} (\lnot t_{x,y,l} \lor p_{x}) \land (\lnot t_{x,y,l} \lor p_{y})$

### Consistance

1.  Toutes les exécutions commencent uniquement à la source.  
	$\bigwedge\limits_{w\in P \cup N} v_{0,0, w} \land \bigwedge\limits_{x=1}^{k} \lnot v_{x,0,w}$

2. Il existe une exécution acceptante pour tous les mots de $P$.  
	$\bigwedge\limits_{w \in P}\bigvee\limits_{x=0}^{k} v_{x, |w|, w} \land a_{x}$
	
	$\bigwedge\limits_{w \in P} \left(\bigvee\limits_{x=0}^{k} x_{x, |w|, w} \right)\land \left(\bigwedge\limits_{x=0}^{k} x_{x, |w|, w} \leftrightarrow (v_{x, |w|, w} \land a_{x}) \right)$
	
	$\bigwedge\limits_{w \in P} \left(\bigvee\limits_{x=0}^{k} x_{x, |w|, w} \right)\land \left(\bigwedge\limits_{x=0}^{k} \left(x_{x, |w|, w} \rightarrow (v_{x, |w|, w} \land a_{x}) \right) \land \left( (v_{x, |w|, w} \land a_{x}) \rightarrow x_{x, |w|, w}\right) \right)$
	
	$\bigwedge\limits_{w \in P} \left(\bigvee\limits_{x=0}^{k} x_{x, |w|, w} \right)\land \left(\bigwedge\limits_{x=0}^{k} \left(\lnot x_{x, |w|, w} \lor (v_{x, |w|, w} \land a_{x}) \right) \land \left( \lnot v_{x, |w|, w} \lor \lnot a_{x} \lor x_{x, |w|, w}\right) \right)$
	
	$\bigwedge\limits_{w \in P} \left(\bigvee\limits_{x=0}^{k} x_{x, |w|, w} \right)\land \left(\bigwedge\limits_{x=0}^{k} (\lnot x_{x, |w|, w} \lor v_{x, |w|, w}) \land (\lnot x_{x, |w|, w} \lor a_{x}) \land \left( \lnot v_{x, |w|, w} \lor \lnot a_{x} \lor x_{x, |w|, w}\right) \right)$

3. Il n'existe pas d'exécution acceptante pour tous les mots de $N$.  
	$\bigwedge\limits_{w \in N} \lnot \bigvee\limits_{x=0}^{k} v_{x, |w|, w}  \land a_{x}$
	
	$\bigwedge\limits_{w \in N}\bigwedge\limits_{x=0}^{k} \lnot v_{x, |w|, w} \lor \lnot a_{x}$

4. Un état est visité s'il y a une transition qui va de l'état visité précédent avec la lettre actuelle vers cet état.  
	$\bigwedge\limits_{w\in P \cup N} \bigwedge\limits_{i=0}^{|w|-1}\bigwedge\limits_{x=0}^{k} v_{x,i,w} \rightarrow \bigwedge\limits_{y=0}^{k} t_{x,y,w[i]} \rightarrow v_{y,i+1,w}$
	
	$\bigwedge\limits_{w\in P \cup N} \bigwedge\limits_{i=0}^{|w|-1}\bigwedge\limits_{x=0}^{k} \lnot v_{x,i,w} \lor \bigwedge\limits_{y=0}^{k} \lnot t_{x,y,w[i]} \lor v_{y,i+1,w}$
	
	$\bigwedge\limits_{w\in P \cup N} \bigwedge\limits_{i=0}^{|w|-1}\bigwedge\limits_{x=0}^{k} \bigwedge\limits_{y=0}^{k} \lnot v_{x,i,w} \lor \lnot t_{x,y,w[i]} \lor v_{y,i+1,w}$

5. Un état ne peut être visité que s’il existe un état précédent qui est également visité et qu’il y a une transition qui lie les deux états.  
	$\bigwedge\limits_{w\in P \cup N}\bigwedge\limits_{i=0}^{|w|-1}\bigwedge\limits_{x=0}^{k} v_{x,i+1,w} \rightarrow \bigvee\limits_{y=0}^{k} t_{y,x,w[i]} \land v_{y,i,w}$
	
	$\bigwedge\limits_{w\in P \cup N}\bigwedge\limits_{i=0}^{|w|-1}\bigwedge\limits_{x=0}^{k} \bigvee\limits_{y=0}^{k} \lnot v_{x,i+1,w} \lor (t_{y,x,w[i]} \land v_{y,i,w})$
	
	$\bigwedge\limits_{w\in P \cup N}\bigwedge\limits_{i=0}^{|w|-1}\bigwedge\limits_{x=0}^{k} \left(\bigvee\limits_{y=0}^{k} \lnot v_{x,i+1,w} \lor y_{x,y,i,w}\right) \land \left(\bigwedge\limits_{y=0}^{k} y_{x,y,i,w} \leftrightarrow (t_{y,x,w[i]} \land v_{y,i,w}) \right)$
	
	$\bigwedge\limits_{w\in P \cup N}\bigwedge\limits_{i=0}^{|w|-1}\bigwedge\limits_{x=0}^{k} \left(\bigvee\limits_{y=0}^{k} \lnot v_{x,i+1,w} \lor y_{x,y,i,w}\right) \land \left(\bigwedge\limits_{y=0}^{k} \left(y_{x,y,i,w} \rightarrow (t_{y,x,w[i]} \land v_{y,i,w})\right) \land \left((t_{y,x,w[i]} \land v_{y,i,w}) \rightarrow y_{x,y,i,w}\right) \right)$
	$\bigwedge\limits_{w\in P \cup N}\bigwedge\limits_{i=0}^{|w|-1}\bigwedge\limits_{x=0}^{k} \left(\bigvee\limits_{y=0}^{k} \lnot v_{x,i+1,w} \lor y_{x,y,i,w}\right) \land \left(\bigwedge\limits_{y=0}^{k} \left(\lnot y_{x,y,i,w} \lor (t_{y,x,w[i]} \land v_{y,i,w})\right) \land \left(\lnot t_{y,x,w[i]} \lor \lnot v_{y,i,w} \lor y_{x,y,i,w}\right) \right)$
	
	$\bigwedge\limits_{w\in P \cup N}\bigwedge\limits_{i=0}^{|w|-1}\bigwedge\limits_{x=0}^{k} \left(\bigvee\limits_{y=0}^{k} \lnot v_{x,i+1,w} \lor y_{x,y,i,w}\right) \land \left(\bigwedge\limits_{y=0}^{k} \left(\lnot y_{x,y,i,w} \lor t_{y,x,w[i]}) \land (\lnot y_{x,y,i,w} \lor v_{y,i,w})\right) \land (\lnot t_{y,x,w[i]} \lor \lnot v_{y,i,w} \lor y_{x,y,i,w}) \right)$

### Déterminisme

1. Les transitions sont unique.  
	$\bigwedge\limits_{l\in \Sigma} \bigwedge\limits_{x=0}^{k}\bigwedge\limits_{y=0}^{k} t_{x,y,l} \rightarrow \lnot \bigvee\limits_{z=0, y\neq z}^{k} t_{x,z,l}$
	
	$\bigwedge\limits_{l\in \Sigma} \bigwedge\limits_{x=0}^{k}\bigwedge\limits_{y=0}^{k} \lnot t_{x,y,l} \lor \lnot \bigvee\limits_{z=0, y\neq z}^{k} t_{x,z,l}$
	
	$\bigwedge\limits_{l\in \Sigma} \bigwedge\limits_{x=0}^{k}\bigwedge\limits_{y=0}^{k} \lnot t_{x,y,l} \lor \bigwedge\limits_{z=0, y\neq z}^{k} \lnot t_{x,z,l}$
	
	$\bigwedge\limits_{l\in \Sigma} \bigwedge\limits_{x=0}^{k}\bigwedge\limits_{y=0}^{k} \bigwedge\limits_{z=0, y\neq z}^{k} \lnot t_{x,y,l} \lor \lnot t_{x,z,l}$

### Complétude

1.  Pour chaque état il doit existé une transition sortante pour chaque lettre de l'alphabet.  
	$\bigwedge\limits_{l\in \Sigma}\bigwedge\limits_{x=0}^{k}\bigvee\limits_{y=0}^{k} t_{x,y,l}$

### Réversibilité

1. Un état ne peut être visité uniquement en partant d'un état et en utilisant une transition inversée. *(vient de la contrainte 5 dans la consistance)*  
	$\bigwedge\limits_{w\in P \cup N} \bigwedge\limits_{i=0}^{|w|-1}\bigwedge\limits_{x=0}^{k} \bigwedge\limits_{y=0}^{k} (\lnot v_{y,i,w} \lor \lnot v_{x,i+1,w} \lor t_{y,x,w[i]}) \land (\lnot v_{y,i,w} \lor \lnot t_{y,x,w[i]} \lor v_{x,i+1,w})$
