# Root robot

## Root robot

* Robot commercialisé par iRobot
* _Coding robot for kids_
* Programmation graphique par blocs (type Scratch)
  ![](src/img/root_coding.png)

## Spécifications

* Protocol _Bluetooth Low Energy_ / _GATT_
    * <https://github.com/RootRobotics/root-robot-ble-protocol>
* SDK disponible en Python mais un peu bugué
* Utilisation synchrone uniquement

## Implémentation

* Bibliothèque asynchone pour manipuler le robot
    * <https://github.com/entwanne/aiorobot>
* Garder une interface la plus simple possible
* Réception et gestion des événements
