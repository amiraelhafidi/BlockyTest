# Teamafspraken BlocklyTest

## Inleiding

Binnen het project BlocklyTest werken we als team samen aan één applicatie.  
Om de kwaliteit van de code, samenwerking en structuur binnen het project te verbeteren, maken we gebruik van branches, merge requests en code reviews in GitLab.

Door duidelijke afspraken te maken over hoe code wordt gecontroleerd en samengevoegd:
- voorkomen we fouten;
- blijft de code overzichtelijk;
- blijft de applicatie stabiel;
- leren teamleden van elkaar.

---

# Git Workflow

## Branches

Iedere developer werkt in een eigen branch die gekoppeld is aan een user story of issue uit GitLab.

Voorbeelden:
- `feature/open-browser-block`
- `feature/login-page`
- `fix/delete-project`

Hierdoor blijft de `main` branch stabiel en overzichtelijk.

Voor iedere nieuwe functionaliteit of bugfix wordt een aparte branch aangemaakt.

---

## Merge Requests

Code mag niet direct naar de `main` branch gepusht worden.  
Iedere wijziging moet eerst via een merge request worden aangeboden.

### Afspraken bij merge requests

- Iedere merge request krijgt een duidelijke titel.
- Een merge request bevat een beschrijving van wat er aangepast is.
- De gekoppelde issue of user story wordt vermeld.
- Eventuele problemen of bijzonderheden worden toegevoegd.
- Merge requests blijven zo klein en overzichtelijk mogelijk.
- Grote wijzigingen worden eerst besproken binnen het team.

### Voor het mergen

Voordat een merge request wordt goedgekeurd:

- moet de functionaliteit getest zijn;
- mogen er geen bekende fouten aanwezig zijn;
- moet gecontroleerd worden of bestaande functionaliteiten blijven werken;
- moet de code compileerbaar en werkend zijn.

---

# Code Reviews

Iedere merge request wordt gecontroleerd door minimaal één teamgenoot.

Tijdens een code review letten we op de volgende onderdelen.

## Functionaliteit

- Werkt de functionaliteit zoals bedoeld?
- Voldoet de code aan de user story?
- Zijn de acceptatiecriteria verwerkt?
- Geeft de applicatie geen errors?

## Codekwaliteit

- Is de code overzichtelijk?
- Zijn functies en variabelen duidelijk benoemd?
- Is er geen onnodige dubbele code?
- Is de oplossing logisch opgebouwd?

## Structuur

- Staat de code in het juiste bestand?
- Zijn routes en templates goed verdeeld?
- Is de projectstructuur netjes?
- Wordt bestaande code goed hergebruikt?

## Database

- Kloppen de SQL-query’s?
- Worden de juiste tabellen gebruikt?
- Worden fouten netjes afgehandeld?
- Blijven relaties tussen tabellen goed werken?

## HTML, CSS en Jinja

- Is de HTML netjes opgebouwd?
- Werkt de Jinja-code goed?
- Past de styling bij de rest van BlocklyTest?
- Werkt de layout goed?

## Gebruikerservaring

- Krijgt de gebruiker duidelijke feedback?
- Zijn knoppen en functies duidelijk?
- Zijn foutmeldingen begrijpelijk?
- Is de pagina gebruiksvriendelijk?

## Security

- Staan er geen API keys of wachtwoorden in de code?
- Wordt invoer gecontroleerd?
- Zijn rechten goed toegepast?

---

# Stijl en Conventies

Binnen het project gebruiken we vaste afspraken zodat de code consistent blijft.

## Python

- Python-code wordt netjes ingesprongen met 4 spaties.
- Variabelen en functies krijgen duidelijke Engelse namen.
- Bestandsnamen beschrijven duidelijk wat het bestand doet.

## Frontend

- HTML en CSS worden netjes geformatteerd.
- De styling blijft consistent binnen BlocklyTest.
- Comments worden alleen gebruikt wanneer extra uitleg nodig is.

## Commit Messages

We gebruiken korte en duidelijke Engelstalige commits.

Voorbeelden:
- `Add login page`
- `Fix delete route`
- `Update overview layout`
- `Add selenium input text block`

---

# Deadlines en Approvals

- Merge requests worden zo vroeg mogelijk aangemaakt.
- Teamgenoten proberen binnen één werkdag feedback te geven.
- Minimaal één teamgenoot moet de code bekijken.
- Feedback wordt verwerkt voordat er gemerged wordt.
- Code moet vóór de sprint review op `main` staan.
- De `main` branch moet altijd een werkende versie van de applicatie bevatten.