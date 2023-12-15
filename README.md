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

### Cohérence

1.  La source est dans l'automate.  
	$p_{0}$

2. Tous les états acceptants font partie de l'automate.  
	$\bigwedge\limits_{x=0}^{k-1}a_{x}\rightarrow p_{x}$
	
	$\bigwedge\limits_{x=0}^{k-1} \lnot a_{x} \lor p_{x}$

3. Toutes les transitions sont valides.  
	$\bigwedge\limits_{x=0}^{k-1}\bigwedge\limits_{y=0}^{k-1}\bigwedge\limits_{l\in\Sigma} t_{x,y,l} \rightarrow p_{x} \land p_{y}$
	
	$\bigwedge\limits_{x=0}^{k-1}\bigwedge\limits_{y=0}^{k-1}\bigwedge\limits_{l\in\Sigma} \lnot t_{x,y,l} \lor (p_{x} \land p_{y})$
	
	$\bigwedge\limits_{x=0}^{k-1}\bigwedge\limits_{y=0}^{k-1}\bigwedge\limits_{l\in\Sigma} (\lnot t_{x,y,l} \lor p_{x}) \land (\lnot t_{x,y,l} \lor p_{y})$

### Consistance

1.  Toutes les exécutions commencent uniquement à la source $(p_0)$.  
	$\bigwedge\limits_{w\in P \cup N} v_{0,0,w}\land \bigwedge\limits_{x=1}^{k-1}\lnot v_{x,0, w}$

2. Pour tous les mots de $P$, il existe une exécution acceptante.  
	$\bigwedge\limits_{w \in P}\bigvee\limits_{x=0}^{k-1} v_{x, |w|, w} \land a_{x}$

 	$\bigwedge\limits_{w \in P} \left(\bigvee\limits_{x=0}^{k-1} x_{x, |w|, w} \right)\land \left(\bigwedge\limits_{x=0}^{k-1} x_{x, |w|, w} \leftrightarrow (v_{x, |w|, w} \land a_{x}) \right)$

 	$\bigwedge\limits_{w \in P} \left(\bigvee\limits_{x=0}^{k-1} x_{x, |w|, w} \right)\land \left(\bigwedge\limits_{x=0}^{k-1} \left(x_{x, |w|, w} \rightarrow (v_{x, |w|, w} \land a_{x}) \right) \land \left( (v_{x, |w|, w} \land a_{x}) \rightarrow x_{x, |w|, w}\right) \right)$

	$\bigwedge\limits_{w \in P} \left(\bigvee\limits_{x=0}^{k-1} x_{x, |w|, w} \right)\land \left(\bigwedge\limits_{x=0}^{k-1} \left(\lnot x_{x, |w|, w} \lor (v_{x, |w|, w} \land a_{x}) \right) \land \left( \lnot v_{x, |w|, w} \lor \lnot a_{x} \lor x_{x, |w|, w}\right) \right)$

	$\bigwedge\limits_{w \in P} \left(\bigvee\limits_{x=0}^{k-1} x_{x, |w|, w} \right)\land \left(\bigwedge\limits_{x=0}^{k-1} (\lnot x_{x, |w|, w} \lor v_{x, |w|, w}) \land (\lnot x_{x, |w|, w} \lor a_{x}) \land \left( \lnot v_{x, |w|, w} \lor \lnot a_{x} \lor x_{x, |w|, w}\right) \right)$
	
4. Pour tous les mots de $N$, il n'existe pas d'exécution acceptante.  
	$\bigwedge\limits_{w \in P}\neg \bigvee\limits_{n=0}^{k-1} v_{x, |w|, w} \land a_{x}$
	
	$\bigwedge\limits_{w \in N}\bigwedge\limits_{n=0}^{k-1} \lnot v_{x, |w|, w} \lor \lnot a_{x}$

5. Une exécution est une suite d'état visité par les transitions.  
	$\bigwedge\limits_{w\in P \cup N} \bigwedge\limits_{i=0}^{|w|-1}\bigwedge\limits_{x=0}^{k-1} v_{x,i,w} \rightarrow \bigwedge\limits_{y=0}^{k-1} t_{x,y,w[i]} \rightarrow v_{y,i+1,w}$
	
	$\bigwedge\limits_{w\in P \cup N} \bigwedge\limits_{i=0}^{|w|-1}\bigwedge\limits_{x=0}^{k-1} \lnot v_{x,i,w} \lor \bigwedge\limits_{y=0}^{k-1} \lnot t_{x,y,w[i]} \lor v_{y,i+1,w}$
	
	$\bigwedge\limits_{w\in P \cup N} \bigwedge\limits_{i=0}^{|w|-1}\bigwedge\limits_{x=0}^{k-1} \bigwedge\limits_{y=0}^{k-1} \lnot v_{x,i,w} \lor \lnot t_{x,y,w[i]} \lor v_{y,i+1,w}$

6. Un état ne peut être visité que s’il existe un état précédent qui est également visité et qu’il y a une transition qui lie les deux états.  
	$\bigwedge\limits_{w\in P \cup N} \bigwedge\limits_{i=0}^{|w|-1}\bigwedge\limits_{x=0}^{k-1} v_{x,i+1,w} \rightarrow \bigvee\limits_{y=0}^{k-1} (t_{y,x,w[i]} \land v_{y,i,w})$
	
	$\bigwedge\limits_{w\in P \cup N} \bigwedge\limits_{i=0}^{|w|-1}\bigwedge\limits_{x=0}^{k-1} \bigvee\limits_{y=0}^{k-1} \lnot v_{x,i+1,w} \lor (t_{y,x,w[i]} \land v_{y,i,w})$
	
	$\bigwedge_{w\in P \cup N}\bigwedge_{i=0}^{|w|-1}\bigwedge_{x=0}^{k-1} \left( \bigvee_{y=0}^{k-1} \lnot v_{x,i+1,w} \lor y_{x,y,i,w} \right) \land \left( \bigwedge_{y=0}^{k-1} y_{x,y,i,w} \leftrightarrow (t_{y,x,w[i]} \land v_{y,i,w}) \right)$
	
	$\bigwedge_{w\in P \cup N}\bigwedge_{i=0}^{|w|-1}\bigwedge_{x=0}^{k-1} \left( \bigvee_{y=0}^{k-1} \lnot v_{x,i+1,w} \lor y_{x,y,i,w} \right) \land \left( \bigwedge_{y=0}^{k-1} ( y_{x,y,i,w} \rightarrow (t_{y,x,w[i]} \land v_{y,i,w}) ) \land ((t_{y,x,w[i]} \land v_{y,i,w}) \rightarrow y_{x,y,i,w}) \right)$

	$\bigwedge_{w\in P \cup N}\bigwedge_{i=0}^{|w|-1}\bigwedge_{x=0}^{k-1} \left( \bigvee_{y=0}^{k-1} \lnot v_{x,i+1,w} \lor y_{x,y,i,w} \right) \land \left( \bigwedge_{y=0}^{k-1} ( \lnot y_{x,y,i,w} \lor (t_{y,x,w[i]} \land v_{y,i,w}) ) \land (\lnot t_{y,x,w[i]} \lor \lnot v_{y,i,w} \lor y_{x,y,i,w}) \right)$
	
	$\bigwedge_{w\in P \cup N}\bigwedge_{i=0}^{|w|-1}\bigwedge_{x=0}^{k-1} \left( \bigvee_{y=0}^{k-1} \lnot v_{x,i+1,w} \lor y_{x,y,i,w} \right) \land \left( \bigwedge_{y=0}^{k-1} ( \lnot y_{x,y,i,w} \lor t_{y,x,w[i]} ) \land (\lnot y_{x,y,i,w} \lor v_{y,i,w}) \land (\lnot t_{y,x,w[i]} \lor \lnot v_{y,i,w} \lor y_{x,y,i,w}) \right)$

### Déterminisme

1. Les transitions sont unique.  
	$\bigwedge\limits_{l\in \Sigma} \bigwedge\limits_{x=0}^{k-1}\bigwedge\limits_{y=0}^{k-1} t_{x,y,l} \rightarrow \lnot \bigvee\limits_{z=0, y\neq z}^{k-1} t_{x,z,l}$
	
	$\bigwedge\limits_{l\in \Sigma} \bigwedge\limits_{x=0}^{k-1}\bigwedge\limits_{y=0}^{k-1} \lnot t_{x,y,l} \lor \lnot \bigvee\limits_{z=0, y\neq z}^{k-1} t_{x,z,l}$
	
	$\bigwedge\limits_{l\in \Sigma} \bigwedge\limits_{x=0}^{k-1}\bigwedge\limits_{y=0}^{k-1} \lnot t_{x,y,l} \lor \bigwedge\limits_{z=0, y\neq z}^{k-1} \lnot t_{x,z,l}$
	
	$\bigwedge\limits_{l\in \Sigma} \bigwedge\limits_{x=0}^{k-1}\bigwedge\limits_{y=0}^{k-1} \bigwedge\limits_{z=0, y\neq z}^{k-1} \lnot t_{x,y,l} \lor \lnot t_{x,z,l}$

### Complétude

1.  Pour chaque état il doit existé une transition sortante pour chaque lettre de l'alphabet.  
	$\bigwedge\limits_{l \in \Sigma} \bigwedge\limits_{x=0}^{k-1} \bigvee\limits_{y=0}^{k-1} t_{x,y,l}$

### Réversibilité

1. Les transitions inversées sont unique.   
	$\bigwedge\limits_{l\in \Sigma} \bigwedge\limits_{x=0}^{k-1}\bigwedge\limits_{y=0}^{k-1} t_{x,y,l} \rightarrow \lnot \bigvee\limits_{z=0, z\neq x}^{k-1} t_{z,y,l}$

	$\bigwedge\limits_{l\in \Sigma} \bigwedge\limits_{x=0}^{k-1}\bigwedge\limits_{y=0}^{k-1} \lnot t_{x,y,l} \lor \lnot \bigvee\limits_{z=0, z\neq x}^{k-1} t_{z,y,l}$

	$\bigwedge\limits_{l\in \Sigma} \bigwedge\limits_{x=0}^{k-1}\bigwedge\limits_{y=0}^{k-1} \lnot t_{x,y,l} \lor \bigwedge\limits_{z=0, z\neq x}^{k-1} \lnot t_{z,y,l}$

	$\bigwedge\limits_{l\in \Sigma} \bigwedge\limits_{x=0}^{k-1}\bigwedge\limits_{y=0}^{k-1} \bigwedge\limits_{z=0, z\neq x}^{k-1} \lnot t_{x,y,l} \lor \lnot t_{z,y,l}$

### Cardinalité des états acceptant

1. le nombre d'états acceptants ne dépasse pas $l$.  
	$\big\lvert \{ x \vert \forall x \in \{0,\dots,k-1\} : a_x \} \big\rvert \leq l$

### Cardinalité des transitions

1. le nombre total de transition dans l'automate est au plus $k'$.  
	$\big\lvert \{ (x, y, l) \, \vert \, \forall x, y \in \{0,\dots,k-1\}, \forall l \in \Sigma : t_{x,y,l} \} \big\rvert \leq k'$

