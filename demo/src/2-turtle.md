# Turtle dans la vraie vie

## Turtle dans la vraie vie

* Diriger une tortue et dessiner
* _Helper_ pour lancer le robot sur une coroutine

```python
#include code/drive.py
```

## Utlisation manuelle

* La lib permet d'utiliser le robot plus directement en instanciant l'objet

```python
#include code/drive_manual.py
```

## Contrôle d'une voiture télécommandée

* Thread tkinter pour récupérer les touches du clavier

```python
#include code/car_tk.py
```

## Contrôle d'une voiture télécommandée

* Thread principal pour gérer les événements du robot
* Utilisation d'une queue pour gérer les interactions
* Les vitesses des moteurs des deux roues sont indépendantes

```python
#include code/car.py
```

## Dessin d'une rosace

* Tracé d'arcs de cercle
* Soumis à quelques imprécisions parfois

```python
#include code/rosace.py
```
