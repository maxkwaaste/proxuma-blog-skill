# -*- coding: utf-8 -*-
import io
def w(p,s): open(p,'w',encoding='utf-8').write(s)
def r(p): return open(p,encoding='utf-8').read()

# ordered (old -> new) per file; long strings first to avoid partial collisions
R = {
'01-market-hero': [
  ('Global managed services market','Wereldwijde markt voor managed services'),
  ('The market more than doubles by 2033.','De markt verdubbelt tegen 2033.'),
  ('Global MSP revenue, 2025 to 2033.','Wereldwijde MSP-omzet, 2025 tot 2033.'),
  ('9.9% CAGR','9,9% CAGR'),
  ('$847.41B','$847 mld'),
  ('by 2033','in 2033'),
  ('$401.15B','$401,15 mld'),
  ('Source: Grand View Research.','Bron: Grand View Research.'),
],
'02-ai-investment': [
  ('Enterprise AI investment','Investering in enterprise-AI'),
  ('Spending roughly tripled in a single year, to $37 billion.','De investering verdrievoudigde in één jaar, naar $37 mld.'),
  ('$11.5B','$11,5 mld'),
  ('$37B','$37 mld'),
  ('3.2&#215; YoY','3,2&#215; in 1 jaar'),
  ('Source: Menlo Ventures, 2025 State of Generative AI in the Enterprise. AI spend flows straight through the MSP channel.',
   'Bron: Menlo Ventures, 2025 State of Generative AI in the Enterprise. AI-budget stroomt recht door het MSP-kanaal.'),
],
'03-data-wall': [
  ('The AI adoption paradox','De AI-adoptieparadox'),
  ('Investment is racing ahead of results.','De investering rent vooruit op de resultaten.'),
  ('Enterprise AI spend','Uitgaven aan enterprise-AI'),
  ('in 2025, roughly 3&#215; year on year','in 2025, ongeveer 3&#215; in één jaar'),
  ('$37B','$37 mld'),
  ('DATA NOT AI-READY','DATA NIET AI-READY'),
  ('The outcome','Het resultaat'),
  ('of AI projects fail to deliver.','van de AI-projecten faalt.'),
  ('Gartner: organizations will abandon 60% of AI projects that lack AI-ready data through 2026.',
   'Gartner: organisaties laten t/m 2026 60% van de AI-projecten zonder AI-ready data vallen.'),
  ('AI is only as good as the data underneath it. The structure has to come first.',
   'AI is alleen zo goed als de data eronder. De structuur komt eerst.'),
  ('Sources: RAND (AI project failure rate); Gartner (AI-ready data).',
   'Bronnen: RAND (faalpercentage AI-projecten); Gartner (AI-ready data).'),
],
'04-revenue-leakage': [
  ('Revenue leakage, an example','Omzetlek, een voorbeeld'),
  ('You secure 215 endpoints. The contract bills for 180.','Je beveiligt 215 endpoints. Het contract factureert er 180.'),
  ('managed &amp; secured','beheerd &amp; beveiligd'),
  ('the contract bills','het contract factureert'),
  ('35 unbilled &#183; ~16% leaked','35 niet gefactureerd &#183; ~16% lek'),
  ('Illustrative. RMM devices, Microsoft 365 licenses and contracted seats drift apart across systems. The work is done; the units never reconcile.',
   'Illustratief. Apparaten in de RMM, Microsoft 365-licenties en gecontracteerde seats lopen tussen systemen uiteen. Het werk is gedaan; de aantallen verzoenen nooit.'),
],
'05-roi-breakdown': [
  ('Where the annual value comes from','Waar de jaarlijkse waarde vandaan komt'),
  ('About $334K to $384K a year, most of it from utilization.','Ongeveer $334K tot $384K per jaar, grotendeels uit benutting.'),
  ('Utilization 65&#8594;72%','Benutting 65&#8594;72%'),
  ('+$196,875','+$196.875'),
  ('Leakage recovery','Teruggewonnen lek'),
  ('+$75,000','+$75.000'),
  ('Scheduling efficiency','Planningsefficiëntie'),
  ('+$37,500','+$37.500'),
  ('SLA breach prevention','SLA-breuk voorkomen'),
  ('On a $3M, 15-engineer MSP, more than a tenth of revenue, recovered from data the MSP already owns.',
   'Bij een MSP van $3 mln met 15 engineers, meer dan een tiende van de omzet, teruggewonnen uit data die de MSP al heeft.'),
  ('per year','per jaar'),
  ('Illustrative model. Drivers partly overlap and are not additive guarantees. An estimate, not a promise. Source: Dxfferent deployment data and cited benchmarks.',
   'Illustratief model. Drivers overlappen deels en zijn geen optelbare garanties. Een schatting, geen belofte. Bron: deployment-data van Dxfferent en geciteerde benchmarks.'),
],
'06-ehr-by-client': [
  ('Engineer Hour Rate (EHR) by client','Engineer Hour Rate (EHR) per klant'),
  ('Same monthly fee. Very different profitability.','Zelfde maandbedrag. Heel andere winstgevendheid.'),
  ('Illustrative, from the worked example. EHR = revenue per engineer-hour. Client A earns barely a third of the others per hour.',
   'Illustratief, uit het rekenvoorbeeld. EHR = omzet per engineer-uur. Klant A verdient per uur amper een derde van de andere twee.'),
  ('$62.50','$62,50'),('$187.50','$187,50'),('/hr','/u'),
  ('Client A','Klant A'),('Client B','Klant B'),('Client C','Klant C'),
  ('underpriced','ondergeprijsd'),
],
'07-capture-vs-show': [
  ("Capturing isn't the same as showing. The &#8722;12% and client margins are illustrative.",
   'Vastleggen is niet hetzelfde als laten zien. De &#8722;12% en klantmarges zijn illustratief.'),
  ('Autotask records every ticket. It surfaces none of the answers.',
   'Autotask legt elk ticket vast. Het toont geen enkel antwoord.'),
  ('Ticket by ticket, captured but never read.','Ticket voor ticket, vastgelegd maar nooit gelezen.'),
  ('Which clients are running below margin?','Welke klanten draaien onder marge?'),
  ('Capture vs. show','Vastleggen vs. laten zien'),
  ('Raw records','Ruwe records'),
  ('Margin by client','Marge per klant'),
  ('below target margin','onder doelmarge'),
  ('Target margin','Doelmarge'),
  ('illustrative','illustratief'),
],
}
for base,reps in R.items():
    s=r(base+'.svg')
    for a,b in reps:
        if a not in s: print('  WARN not found in',base,':',a[:40])
        s=s.replace(a,b)
    w(base+'-nl.svg', s)
    print('wrote', base+'-nl.svg')
