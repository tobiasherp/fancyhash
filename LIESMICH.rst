
===========================================
FancyHash - Hashwerte berechenen und prüfen
===========================================

Fancyhash berechnet alle Hashwerte, die von Python unterstützt werden.

Auf Linuxsystemen ist die Berechnung von Hashwerten normalerweise kein großes
Problem - Programme wie md5sum, sha1sum usw. werden standardmäßig installiert,
oder sie können sehr einfach mit einem gut bekannten Standardpaket installiert
werden.  Windows(tm)-Anwender haben es deutlich schwerer, ein passendes
Programm zu finden.

Außerdem bekommen Sie oft keine ordentliche <programm>.md5-Datei, die
ordentliche ``<hash> *<programm>``-Zeilen enthält, sondern nur den nackten
Hashwert - manchmal sogar in großbuchstabiger Hex-Darstellung!
Ja, man kann sich helfen, und vim kann Groß- mittels ~-Kommando in
Kleinschreibung umwandeln; aber das ist umständlich und mit fancyhash auch
unnötig.  Sie haben die Datei heruntergeladen, und Sie speichern den Hashwert
in einer Datei, deren Erweiterung Sie passend erweitern - das war's: fancyhash
wird sie verarbeiten.  Wie z. B. auch gpg wird es den Dateinamen erraten, indem
es die letzte Komponente der Erweiterung streicht.

Ach, und wo wir gerade dabei sind:  Manche Dateien sind ziemlich groß, und die
Berechnung des Hashwerts dauert eine Weile.  Also, warum die Wartezeit nicht ein
bißchen auflockern ...
