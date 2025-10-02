import json
from pathlib import Path

translations = {
    # mammals
    'loxodonta_africana': {
        'habitat': 'Savany, travnaté pláně a řídké lesy napříč subsaharskou Afrikou.',
        'funFact': 'Stáda vedená matriarchou si předávají informace infrazvukovým duněním slyšitelným na kilometry daleko.'
    },
    'balaenoptera_musculus': {
        'habitat': 'Pelagické vody všech oceánů; mezi krmišti a místy rozmnožování migruje podle ročních období.',
        'funFact': 'Jeho srdce je velké zhruba jako menší automobil a při hlubokém ponoru tluče jen několikrát za minutu.'
    },
    'ailuropoda_melanoleuca': {
        'habitat': 'Chladnější horské bambusové lesy v čínských provinciích S’-čchuan, Šen-si a Kan-su.',
        'funFact': 'Pandí „pseudopalec“ je zvětšená zápěstní kost, která jí umožňuje obratně loupat bambusové stvoly.'
    },
    'panthera_tigris_tigris': {
        'habitat': 'Mangrovy, travnaté porosty a lesy v Indii, Bangladéši, Nepálu a Bhútánu.',
        'funFact': 'Kresba pruhů je u každého tygra jedinečná a slouží jako otisk prstu, když se skrývá při lovu.'
    },
    'canis_lupus': {
        'habitat': 'Lesy, tundru, pouště i horské oblasti napříč Severní Amerikou a Eurasií.',
        'funFact': 'Vytí vlků se může nést více než deset kilometrů a pomáhá smečce při lovu i obraně teritoria.'
    },
    'ursus_maritimus': {
        'habitat': 'Arktický mořský led, pobřežní fjordy a ostrovy kolem severního pólu.',
        'funFact': 'Duté průsvitné chlupy spolu se silnou vrstvou tuku chrání medvědy i v bouřích s mrazem kolem −40 °C.'
    },
    'phascolarctos_cinereus': {
        'habitat': 'Eukalyptové háje podél východního a jižního pobřeží Austrálie.',
        'funFact': 'Koaly prospí až dvacet hodin denně, aby ušetřily energii potřebnou na trávení vláknitých listů eukalyptu.'
    },
    'osphranter_rufus': {
        'habitat': 'Otevřené pláně, stepi a polopouště ve střední Austrálii.',
        'funFact': 'Silné zadní nohy umožní samcům přeskočit devítimetrovou vzdálenost, zatímco ocas slouží jako vyvažující třetí opora.'
    },
    'pongo_pygmaeus': {
        'habitat': 'Nízké tropické deštné lesy ostrova Borneo.',
        'funFact': 'Orangutani si každý večer vysoko v korunách z větví a listí stavějí nový noční pelíšek.'
    },
    'hippopotamus_amphibius': {
        'habitat': 'Pomalu tekoucí řeky, jezera a mokřiny napříč subsaharskou Afrikou.',
        'funFact': 'Hroši vylučují oranžovou „krví připomínající“ tekutinu, která funguje jako přírodní opalovací krém i dezinfekce.'
    },
    'panthera_leo': {
        'habitat': 'Savany a prosvětlené lesy východní a jižní Afriky.',
        'funFact': 'Lvi jsou jediné skutečně společenské kočkovité šelmy; žijí v tlupách, které společně odchovávají mláďata.'
    },
    'acinonyx_jubatus': {
        'habitat': 'Otevřené travnaté pláně a polopouště subsaharské Afriky.',
        'funFact': 'Polozatahovací drápy a pružná páteř dovolují gepardům vyvinout rychlost přes 100 km/h.'
    },
    'gorilla_beringei_beringei': {
        'habitat': 'Mlžné horské lesy masivu Virunga a neprostupného pralesa Bwindi.',
        'funFact': 'Po večerním hledání potravy si každá gorila staví na zemi nové lůžko z větví a listů.'
    },
    'panthera_uncia': {
        'habitat': 'Strmé skalní svahy a alpské louky střední a jižní Asie.',
        'funFact': 'Ocas sněžného leoparda je téměř stejně dlouhý jako tělo a při odpočinku se kolem něj ovíjí jako huňatá šála.'
    },
    'vulpes_lagopus': {
        'habitat': 'Tundra a zaledněná pobřeží napříč celou arktickou oblastí.',
        'funFact': 'Hustá srst mění barvu ze letní hnědé na zimní bílou a dokonale tak maskuje lišku polární.'
    },
    'ornithorhynchus_anatinus': {
        'habitat': 'Sladkovodní potoky, jezírka a řeky ve východní Austrálii a na Tasmánii.',
        'funFact': 'Samci ptakopysků mají na zadních nohách jedové ostruhy, jimiž dokážou zasadit bolestivé řezné bodnutí.'
    },
    'tursiops_truncatus': {
        'habitat': 'Pobřežní i otevřené vody mírného a tropického pásma po celém světě.',
        'funFact': 'Každý delfín si vytváří charakteristické písknutí, které funguje jako jeho jméno.'
    },
    'bradypus_variegatus': {
        'habitat': 'Nízké vlhké lesy od Hondurasu až po severní Argentinu.',
        'funFact': 'Lenochodi tráví většinu života hlavou dolů a jen jednou za týden sestupují na zem, aby se vyprázdnili.'
    },
    'myrmecophaga_tridactyla': {
        'habitat': 'Savany, mokřady a tropické lesy Střední a Jižní Ameriky.',
        'funFact': 'Jeho štíhlý jazyk dokáže šlehnout až 160krát za minutu a stírá z mravenišť mravence i termity.'
    },
    'vombatus_ursinus': {
        'habitat': 'Soustavy podzemních nor v lesích a vřesovištích jihovýchodní Austrálie.',
        'funFact': 'Vombati vyrábějí kostkovitý trus, který skládají do úhledných hromádek, aby vyznačili své území.'
    },
    'lycaon_pictus': {
        'habitat': 'Savany, otevřené lesy a křovinatá buš v subsaharské Africe.',
        'funFact': 'Členové smečky se dělí o kořist tak, že ji zvracejí mláďatům i zraněným jedincům.'
    },
    'alces_alces': {
        'habitat': 'Boreální lesy, rašeliniště a okraje tundry v severní části Ameriky a Eurasie.',
        'funFact': 'Samci každý rok znovu dorůstají mohutné lopatovité parohy, které mohou měřit i více než 1,8 metru.'
    },
    'bison_bison': {
        'habitat': 'Prérie, otevřené pláně a říční údolí napříč Severní Amerikou.',
        'funFact': 'Přestože váží stovky kilogramů, dokážou bizoni bleskově manévrovat a rozběhnout se až na 55 km/h.'
    },
    'suricata_suricatta': {
        'habitat': 'Suché křovinaté oblasti a savany jižní Afriky.',
        'funFact': 'Skupiny surikat se střídají ve službě hlídače a používají různé signály pro různá nebezpečí.'
    },
    'vulpes_vulpes': {
        'habitat': 'Lesy, zemědělskou krajinu, okraje tundry i městské parky napříč severní polokoulí.',
        'funFact': 'Lišky červené lokalizují kořist pod sněhem díky jemným vibracím, které zachytí dřív, než skočí.'
    },
    'okapia_johnstoni': {
        'habitat': 'Hustý podrost deštného pralesa Ituri v Demokratické republice Kongo.',
        'funFact': 'Chápavý jazyk okapi je tak dlouhý, že si s ním zvíře dokáže olíznout víčka i vyčistit uši.'
    },
    'trichechus_manatus': {
        'habitat': 'Teplé mělké pobřežní vody, ústí řek a sladkovodní prameny v Karibiku a jihovýchodních státech USA.',
        'funFact': 'Kapustňáci denně spasou až deset procent své hmotnosti v mořské trávě, aby pokryli pomalý metabolismus.'
    },
    'capra_ibex': {
        'habitat': 'Strmé skalnaté svahy nad hranicí lesa v celých Alpách.',
        'funFact': 'Samci se během říje srážejí metrovými, rýhovanými rohy i na úzkých horských římsách.'
    },
    'sarcophilus_harrisii': {
        'habitat': 'Suché lesy, listnaté háje a pastviny Tasmánie.',
        'funFact': 'Tasmánský ďábel vydává při krmení hlasité skřeky, kterými zastrašuje soupeře u kořisti.'
    },
    'monodon_monoceros': {
        'habitat': 'Chladné pobřežní vody Arktidy kolem Kanady, Grónska, Špicberků a Ruska.',
        'funFact': 'Samčí kel je prodloužený špičák prorostlý nervy; narval jím testuje teplotu a slanost vody.'
    },
    'amphiprion_ocellaris': {
        'habitat': 'Mělké laguny a korálové útesy Indického a západního Pacifiku.',
        'funFact': 'Klauni žijí v symbióze s mořskými sasankami, jejichž žahavé chapadlo jim poskytuje útočiště.'
    },
    'carcharodon_carcharias': {
        'habitat': 'Pobřežní vody mírných pásem všech oceánů.',
        'funFact': 'Žraloci bílí dokážou při útoku z vody vyskočit a uchopit kořist i několik metrů nad hladinou.'
    },
    'rhincodon_typus': {
        'habitat': 'Teplé tropické moře otevřeného oceánu i pobřežních oblastí po celém světě.',
        'funFact': 'Ačkoli je největší rybou na planetě, filtruje potravu – plankton a malé rybky – přes široká ústa.'
    },
    'pygocentrus_nattereri': {
        'habitat': 'Pomalé řeky, záplavová jezera a meandrové laguny povodí Amazonky a Orinoka.',
        'funFact': 'Hejna piranh ostrými, do sebe zapadajícími zuby vyrýhují z kořisti kusy masa a útočí v krátkých, koordinovaných salvách.'
    },
    'salmo_salar': {
        'habitat': 'Severní Atlantik a sladkovodní řeky, do nichž se vrací na tření.',
        'funFact': 'Lososi atlantičtí využívají magnetické pole Země i pachové stopy, aby našli rodný tok.'
    },
    'pterois_volitans': {
        'habitat': 'Tropické indo-pacifické útesy; introdukované populace žijí v západním Atlantiku a Karibiku.',
        'funFact': 'Pruhovaná hřbetní pera obsahují jedovaté trny, které dokážou bolestivě zasáhnout predátora.'
    },
    'mobula_birostris': {
        'habitat': 'Otevřený tropický a subtropický oceán po celém světě, často poblíž korálových útesů.',
        'funFact': 'Manta občas vyskočí vysoko nad hladinu a dopadem hlasitě pleskne – patrně jako signál ostatním.'
    },
    'hippocampus_kuda': {
        'habitat': 'Mořské louky, mangrovy a korálové zahrady Indického oceánu a západního Pacifiku.',
        'funFact': 'Samci mořských koníků nosí oplodněná vajíčka v břišním vaku a vypouštějí již vyvinutá mláďata.'
    },
    'sphyrna_mokarran': {
        'habitat': 'Teplé pobřežní vody, kontinentální šelfy a korálové útesy tropických a subtropických moří.',
        'funFact': 'Rozšířená hlavová „kladiva“ fungují jako křídla, takže žralok může přitlačit rejnoky k dnu, než udeří.'
    },
    'prionace_glauca': {
        'habitat': 'Otevřené vody mírných i tropických oceánů, často sleduje proudy napříč celými pánvemi.',
        'funFact': 'Dlouhé, srpovité prsní ploutve a štíhlé tělo mu umožňují migrovat tisíce kilometrů mezi lovišti a porodními oblastmi.'
    },
    'electrophorus_electricus': {
        'habitat': 'Bahnitá ramena a zaplavované lesy povodí Amazonky a Orinoka.',
        'funFact': 'Električtí úhoři dokážou vyslat výboj přes 600 voltů, kterým ohromí kořist i útočníky.'
    },
    'latimeria_chalumnae': {
        'habitat': 'Strmé sopečné svahy v hloubkách u Komorských ostrovů a v Indonésii.',
        'funFact': 'Latimérie byla považována za vyhynulou až do roku 1938; její ploutve připomínají končetiny prvních čtyřnožců.'
    },
    'mola_mola': {
        'habitat': 'Mírné a tropické oceány, kde se vyhřívá u hladiny a střídavě sestupuje za medúzami.',
        'funFact': 'Samice měsíčníka dokáže vypustit i více než 300 milionů jiker během jediného tření.'
    },
    'hippoglossus_hippoglossus': {
        'habitat': 'Chladné hlubší vody kontinentálních šelfů severního Atlantiku.',
        'funFact': 'Mladí halibuti plavou vzpřímeně, ale s věkem se obě oči přesunou na pravou stranu těla a ryba pak leží na dně.'
    },
    'betta_splendens': {
        'habitat': 'Mělké rýžové zavlažovací kanály a tůňky v Thajsku, Kambodži a Vietnamu.',
        'funFact': 'Samci bojnic staví pěnová hnízda na hladině a neúnavně hlídají snůšku i potěr.'
    },
    'thunnus_thynnus': {
        'habitat': 'Severní Atlantik a Středozemní moře, kde podniká dálkové migrace mezi trdlišti a lovišti.',
        'funFact': 'Protiproudové cévní uspořádání pomáhá tuňáku obecnému udržet tělesnou teplotu nad okolní mořskou vodou.'
    },
    'mitsukurina_owstoni': {
        'habitat': 'Hluboké pelagické vody západního Pacifiku a Atlantiku, obvykle 200–1300 m pod hladinou.',
        'funFact': 'Žralok skřetovitý má vystřelovací čelisti, kterými během zlomku sekundy uchopí kořist jako z pasti.'
    },
    'melanocetus_johnsonii': {
        'habitat': 'Temné pelagické zóny Atlantiku a Pacifiku v hloubkách přes kilometr.',
        'funFact': 'Samice si na hřbetě nese světélkující návnadu, zatímco drobní samci s ní splývají v parazitickém svazku.'
    },
    'exocoetus_volitans': {
        'habitat': 'Teplá otevřená moře mezi 40° severní a jižní šířky.',
        'funFact': 'Rychlým švihem ocasní ploutve a roztáhnutými prsními „křídly“ dokáže létavka klouzat desítky metrů nad hladinou.'
    },
    'gadus_morhua': {
        'habitat': 'Kontinentální šelfy severního Atlantiku od Newfoundlandu po Barentsovo moře.',
        'funFact': 'Tresky obecné tvoří v zimě obrovská třecí hejna, která po staletí přitahovala rybářské flotily.'
    },
    'oncorhynchus_mykiss': {
        'habitat': 'Chladné čisté řeky, jezera a příbřežní toky Severní Ameriky; hojně introdukován i na dalších kontinentech.',
        'funFact': 'Některé populace tráví dospělost v moři jako tzv. steelhead a na tření se vracejí do rodných toků.'
    },
    'somniosus_microcephalus': {
        'habitat': 'Hluboké, ledové vody severního Atlantiku a arktických moří.',
        'funFact': 'Žraloci grónští rostou méně než jeden centimetr za rok a patří k nejdéle žijícím obratlovcům.'
    },
    'pomacanthus_imperator': {
        'habitat': 'Korálové útesy a strmé lagunové stěny Indo-Pacifiku od východní Afriky po Polynésii.',
        'funFact': 'Mladí císařští bodloci mají soustředné modrobílé kruhy, které se v dospělosti změní na žluté a safírové pruhy.'
    },
    'silurus_glanis': {
        'habitat': 'Pomalu tekoucí velké řeky a jezera Evropy a západní Asie.',
        'funFact': 'Sumec velký dokáže polykat vzduch na hladině, aby přežil ve vodě chudé na kyslík, a občas zaskočí vodní ptáky.'
    },
    'danio_rerio': {
        'habitat': 'Mělce proudící potoky a rýžové polní kanály v povodí Gangy a Brahmaputry.',
        'funFact': 'Průsvitná embrya a rychlý vývoj udělaly ze zebřičky pruhované základní model v genetice a regenerativním výzkumu.'
    },
    'lates_niloticus': {
        'habitat': 'Velká africká jezera a hlavní toky v povodí Nilu, zejména jezero Viktoriino.',
        'funFact': 'Mladí okouni nilští se drží ve školkách v mělkých zátokách, zatímco dospělci loví osamoceně z úkrytu.'
    },
    'istiophorus_platypterus': {
        'habitat': 'Teplé a mírné vody Atlantského a Indopacifického oceánu.',
        'funFact': 'Plachetníci dokážou zrychlit přes 100 km/h a sklopením hřbetní ploutve snižují odpor vody.'
    },
    'cetorhinus_maximus': {
        'habitat': 'Chladnější šelfové vody severního Atlantiku i mírného pásma jižní polokoule.',
        'funFact': 'Žralok veliký filtruje plankton tak, že každou hodinu přečerpá více než 2 000 litrů mořské vody.'
    },
    'cheilinus_undulatus': {
        'habitat': 'Korálové útesy Indického oceánu a západního Pacifiku.',
        'funFact': 'Pyskoun napoleonský je protogynní – většina jedinců začne život jako samice a později se může změnit na samce.'
    },
    'salvelinus_alpinus': {
        'habitat': 'Ledovcovová jezera a chladné řeky severních oblastí Evropy, Asie i Ameriky.',
        'funFact': 'Siven alpský snáší nižší teploty než většina ryb a udržuje aktivitu i ve vodě těsně nad bodem mrazu.'
    },
    'ambystoma_mexicanum': {
        'habitat': 'Chladné kanály a zbytky jezerní soustavy Xochimilco v Mexico City.',
        'funFact': 'Axolotli zůstávají v larválním stadiu a zvládnou znovu dorůst končetin, části míchy i srdeční tkáně.'
    },
    'dendrobates_tinctorius': {
        'habitat': 'Deštné pralesy Guyany, Surinamu a severní Brazílie.',
        'funFact': 'Toxiny z mravenčí potravy dělají z pralesničky jedné z nejjedovatějších žab tropů.'
    },
    'agalychnis_callidryas': {
        'habitat': 'Vlákna tropických deštných lesů od jižního Mexika po Kolumbii.',
        'funFact': 'Když se vyplaší, rozbliká rudé oči a výrazné boční pruhy, aby zmátla predátora, než odskočí do bezpečí.'
    },
    'salamandra_salamandra': {
        'habitat': 'Vlhké listnaté lesy a prameniště střední a jižní Evropy.',
        'funFact': 'Parotidní žlázy za očima vylučují silné alkaloidní toxiny, jakmile se mlok cítí ohrožen.'
    },
    'rhinella_marina': {
        'habitat': 'Travnaté pláně, zahrady a městské okraje od Mexika po Amazonii; na mnoha místech je invazní.',
        'funFact': 'Rozsáhlé jedové žlázy jim umožňují odrazit většinu predátorů a způsobují potíže zavlečeným ekosystémům.'
    },
    'notophthalmus_viridescens': {
        'habitat': 'Lesní rybníky a mokřady ve východní části Severní Ameriky.',
        'funFact': 'Vývoj prochází vodní larvou, jasně oranžovým suchozemským „eftem“ a nakonec opět vodní dospělou fází.'
    },
    'cryptobranchus_alleganiensis': {
        'habitat': 'Chladné, dobře okysličené řeky Apalačských a Ozarkských hor.',
        'funFact': 'Tyto obří „pekelné mloky“ dýchají především přes zvrásněnou kůži a potřebují neustálý proud vody.'
    },
    'andrias_davidianus': {
        'habitat': 'Rychlé horské potoky a řeky střední a jižní Číny.',
        'funFact': 'Čínský velemlok může dorůst přes 1,5 metru a vydává pronikavé zvuky připomínající dětský pláč.'
    },
    'hyalinobatrachium_valerioi': {
        'habitat': 'Listy nad potoky v nížinných deštných lesích Střední Ameriky.',
        'funFact': 'Samci hlídají vajíčka na spodní straně listu a zvlhčují je, aby zůstala průsvitná a nevysychala.'
    },
    'ambystoma_tigrinum': {
        'habitat': 'Trávníky, lesy a prérie severní Ameriky s přístupem k mělkým tůním.',
        'funFact': 'Larvy mohou při vysychání rybníka vyvinout zvětšené hlavy a zuby a přejít do kanibalistické formy.'
    },
    'bombina_orientalis': {
        'habitat': 'Mělké rybníčky, rýžoviště a lesní tůně severovýchodní Číny a Korejského poloostrova.',
        'funFact': 'Při ohrožení se prohne do obranného postoje a ukáže nachové břicho varující před toxiny v kůži.'
    },
    'proteus_anguinus': {
        'habitat': 'Vápencové podzemní toky Dinárských Alp.',
        'funFact': 'Slepý mlok jeskynní se dožívá více než 70 let a dokáže vydržet bez potravy i několik let.'
    },
    'pipa_pipa': {
        'habitat': 'Pomalu tekoucí vody a zaplavované pralesy severní Jižní Ameriky.',
        'funFact': 'Samice nosí oplodněná vajíčka v jamkách na hřbetě, odkud se líhnou plně vyvinutá mláďata.'
    },
    'xenopus_laevis': {
        'habitat': 'Stojaté či pomalu tekoucí vody jižní Afriky.',
        'funFact': 'Drápatky byly kdysi využívány k těhotenským testům: lidská moč spustila u samic kladení vajec.'
    },
    'pyxicephalus_adspersus': {
        'habitat': 'Sezónně zaplavované savany a pastviny střední a jižní Afriky.',
        'funFact': 'Samci stráží tisíce pulců a v případě potřeby vyhrabou odtokový žlab, aby tůň nevyschla.'
    },
    'oophaga_pumilio': {
        'habitat': 'Tropické pralesy Karibské strany Střední Ameriky.',
        'funFact': 'Samice odnášejí pulce do bromélií a dokrmují je neplodnými vajíčky bohatými na živiny.'
    },
    'pleurodeles_waltl': {
        'habitat': 'Stojaté nádrže, zavlažovací kanály a pomalu tekoucí vody Pyrenejského poloostrova a Maroka.',
        'funFact': 'Při napadení prohne hřbet tak, že ostrá žebra proniknou kůží a vstříknou predátorovi jed.'
    },
    'rhacophorus_nigropalmatus': {
        'habitat': 'Deštné lesy Bornea, kde se zdržuje vysoko na stromech.',
        'funFact': 'Plovací blány na prstech fungují jako padák a žába s nimi dokáže klouzat několik desítek metrů.'
    },
    'conraua_goliath': {
        'habitat': 'Pralesní potoky Kamerunu a Rovníkové Guineje s vodopády a balvany.',
        'funFact': 'Největší žába světa si staví hnízda z kamínků a hlídá snůšku jako pečlivý rodič.'
    },
    'phyllobates_terribilis': {
        'habitat': 'Mlžné pralesy na pacifickém pobřeží Kolumbie.',
        'funFact': 'Jedna kůže pralesničky strašné obsahuje dost batrachotoxinu na usmrcení několika lidí.'
    },
    'ambystoma_maculatum': {
        'habitat': 'Listnaté lesy a periodické tůně ve východní části Severní Ameriky.',
        'funFact': 'Embrya sdílejí symbiózu se zelenými řasami, které uvnitř vajec vyrábějí kyslík.'
    },
    'pseudacris_crucifer': {
        'habitat': 'Vlhké lesy a mokřady severovýchodní Ameriky.',
        'funFact': 'Jejich jarní sbor je jedním z prvních zvuků probouzejícího se lesa po zimě.'
    },
    'taricha_torosa': {
        'habitat': 'Potoky a lesy pobřežní Kalifornie.',
        'funFact': 'Kalifornský čolek má pokožku s tetrodotoxinem – jeden jedinec může otrávit dospělého člověka.'
    },
    'siphonops_annulatus': {
        'habitat': 'Vlhká půda tropických lesů Brazílie a sousedních zemí.',
        'funFact': 'Matky červorů se nechávají okusovat mláďaty; kůže jim po tomto „kojení“ znovu dorůstá.'
    },
    'lithobates_catesbeianus': {
        'habitat': 'Jezírka, mokřady a pomalu tekoucí vody východu Severní Ameriky a mnoha zavlečených oblastí.',
        'funFact': 'Jeho hluboké volání „jug-o-rum“ je slyšet na více než kilometr daleko.'
    },
    'atelopus_zeteki': {
        'habitat': 'Horská údolí panamských deštných pralesů se studenými bystřinami.',
        'funFact': 'Samci varují houpavým „vlněním“ předních nohou, protože hluk vodopádu přehlušuje jejich hlas.'
    },
    'bufo_bufo': {
        'habitat': 'Zahrady, lesy a mokřady napříč Evropou a západní Asií.',
        'funFact': 'Obranná jedová žláza parotida dokáže odradit i velkého predátora.'
    },
    'spea_hammondii': {
        'habitat': 'Suché louky, dubové savany a dočasné kaluže Kalifornie a severní Baja California.',
        'funFact': 'Na zadních nohách má tvrdé rohovité špice, jimiž se bleskově zavrtá dozadu do vlhké země.'
    },
    'lithobates_sylvaticus': {
        'habitat': 'Jehličnaté i listnaté lesy Kanady a severu USA.',
        'funFact': 'Skokan lesní snese promrznutí až dvou třetin tělesné vody a na jaře se znovu probudí k životu.'
    },
    'rana_temporaria': {
        'habitat': 'Louky, zahrady a lesy téměř po celé Evropě a části Asie.',
        'funFact': 'V zimě přečkává zahrabaná v bahně nebo listí a dokáže dýchat i skrze pokožku.'
    },
    'varanus_komodoensis': {
        'habitat': 'Suché lesy a travnaté svahy ostrovů Komodo, Rinca, Flores a Gili Motang.',
        'funFact': 'Slina varana komodského obsahuje směs bakterií a toxinů, takže i jediné kousnutí může být smrtelné.'
    },
    'chelonia_mydas': {
        'habitat': 'Povodí tropických a subtropických moří s mořskými loukami a korálovými útesy.',
        'funFact': 'Dospělá kareta obrovská se živí převážně mořskými řasami a její tuk pak zbarvuje maso do zelena.'
    },
    'ophiophagus_hannah': {
        'habitat': 'Deštné lesy a bambusové houštiny jižní a jihovýchodní Asie.',
        'funFact': 'Královská kobra staví hnízdo z listí a jako jediný had hlídá snůšku vajec.'
    },
    'heloderma_suspectum': {
        'habitat': 'Pouště, křoviny a kamenné svahy jihozápadu USA a severního Mexika.',
        'funFact': 'Korovec jedovatý má jedové žlázy ve spodní čelisti; jed stéká po rýhovaných zubech do rány.'
    },
    'crocodylus_niloticus': {
        'habitat': 'Řeky, jezera a mokřady subsaharské Afriky.',
        'funFact': 'Matky hlídají hnízdo a po vylíhnutí přenášejí mláďata v tlamě do bezpečné vody.'
    },
    'chelonoidis_niger': {
        'habitat': 'Vulkanické trávníky a vlhké vysočiny souostroví Galapágy.',
        'funFact': 'Galapážské želvy mohou vážit přes 250 kilogramů a dožít se více než sta let.'
    },
    'pogona_vitticeps': {
        'habitat': 'Suchá křovinatá buš a skalnaté oblasti vnitrozemí Austrálie.',
        'funFact': 'Vousatá agama zvednutím a zčernáním krčního límce varuje rivaly i predátory.'
    },
    'dermochelys_coriacea': {
        'habitat': 'Otevřené tropické a mírné oceány po celém světě.',
        'funFact': 'Kožatka může během jediného roku přeplout celý Atlantik mezi hnízdišti a lovišti medúz.'
    },
    'alligator_mississippiensis': {
        'habitat': 'Pomalu tekoucí řeky, bažiny a ústí v jihovýchodních státech USA.',
        'funFact': 'Alligátoři používají teplé i studené jámy v hnízdě, aby upravili pohlaví mláďat.'
    },
    'chlamydosaurus_kingii': {
        'habitat': 'Suché savany a otevřené lesy severní Austrálie a jižní Papuy.',
        'funFact': 'Když se cítí ohrožena, roztáhne límcovitý záhyb kolem hlavy a hlasitě syčí.'
    },
    'furcifer_pardalis': {
        'habitat': 'Pobřežní lesy a plantáže na Madagaskaru.',
        'funFact': 'Chameleoni pardálí mění barvy podle nálady a teploty; samci při námluvách svítí jasnými odstíny.'
    },
    'python_regius': {
        'habitat': 'Travnaté savany a okraje lesů západní a střední Afriky.',
        'funFact': 'Při ohrožení se krajta královská stočí do těsného klubka a schová hlavu uprostřed.'
    },
    'crotalus_atrox': {
        'habitat': 'Pouště, křoviny a pastviny jihozápadu USA a severního Mexika.',
        'funFact': 'Chřestýši rozechvívají rohovité segmenty na konci ocasu až devadesátkrát za sekundu jako varovný bzučák.'
    },
    'cyclura_lewisi': {
        'habitat': 'Vápencové skalnaté svahy a pobřežní křoviny ostrova Grand Cayman.',
        'funFact': 'Leguáni modří jsou kriticky ohroženi; dospělí samci mohou mít kobaltově modré zbarvení.'
    },
    'moloch_horridus': {
        'habitat': 'Písečné pouště a spinifexové pláně západní a centrální Austrálie.',
        'funFact': 'Trnitý ďábel dokáže vést vodu po kapilárách mezi šupinami až k tlamě.'
    },
    'boa_constrictor': {
        'habitat': 'Tropické lesy a suché savany od Mexika po Argentinu.',
        'funFact': 'Hroznýš královský loví ze zálohy a kořist usmrtí utažením těla, nikoli udušením.'
    },
    'eunectes_murinus': {
        'habitat': 'Pomalu tekoucí řeky, oxbow jezera a zaplavované mokřady Amazonie.',
        'funFact': 'Anakonda velká je aktivní i v noci a dokáže pozřít kapybaru či kajmana.'
    },
    'amblyrhynchus_cristatus': {
        'habitat': 'Pobřežní lávové pobřeží Galapág, kde se sluní na kamenech.',
        'funFact': 'Leguáni mořští při potápění polykají mořské řasy a přebytečnou sůl vypšikávají nosními žlázami.'
    },
    'gekko_gecko': {
        'habitat': 'Vlhké tropické lesy jihovýchodní Asie, často i na budovách.',
        'funFact': 'Tlapky tokaje jsou posety mikroskopickými lamelami, díky nimž přilne k hladkým stěnám.'
    },
    'caretta_caretta': {
        'habitat': 'Teplé mírné a subtropické oceány s písčitými plážemi vhodnými k hnízdění.',
        'funFact': 'Dospělci podnikají tisícikilometrové migrace mezi lovišti a rodnými plážemi, kam se samice vrací klást vejce.'
    },
    'macrochelys_temminckii': {
        'habitat': 'Bahnitá dna řek a jezer jihovýchodních Spojených států.',
        'funFact': 'Kajmanka dravá láká ryby růžovým výrůstkem na jazyku, který napodobuje červa.'
    },
    'dendroaspis_polylepis': {
        'habitat': 'Savany a křoviny subsaharské Afriky.',
        'funFact': 'Mamba černá patří k nejrychlejším hadům a její neurotoxin může zabít během několika hodin.'
    },
    'terrapene_carolina': {
        'habitat': 'Lesní okraje, louky a zahrady východních Spojených států.',
        'funFact': 'Boxovací želva má kloubový plastron, který jí dovolí zcela uzavřít krunýř.'
    },
    'phrynosoma_cornutum': {
        'habitat': 'Polopouště, chaparral a mezquiteové porosty Texasu a severního Mexika.',
        'funFact': 'Leguánek rohatý může v krajním případě vystřelit z očních koutků kapky krve, aby odradil predátora.'
    },
    'varanus_salvadorii': {
        'habitat': 'Bažinaté nížinné lesy a mangrovy Nové Guineje.',
        'funFact': 'Varan krokodýlí může měřit přes dva a půl metru a má nejdelší ocas ze všech ještěrů.'
    },
    'bitis_gabonica': {
        'habitat': 'Deštné pralesy a plantáže západní a střední Afriky.',
        'funFact': 'Zmije gabunská má nejdelší jedové zuby mezi hady a útočí z klidu bleskovým výpadem.'
    },
    'caiman_crocodilus': {
        'habitat': 'Pomalu tekoucí řeky, meandrová jezera a zaplavované mokřady od Mexika po Brazílii.',
        'funFact': 'Kostěný hřeben nad očima připomíná brýle a stíní, když číhá na kořist těsně pod hladinou.'
    },
    'varanus_varius': {
        'habitat': 'Eukalyptové lesy a písečné duny východní Austrálie.',
        'funFact': 'Varan krajkový je obratný šplhavec a uloví i mláďata klokanů nebo ptáky hnízdící na stromech.'
    },
    'python_bivittatus': {
        'habitat': 'Bažiny, rýžoviště a řidší lesy jihovýchodní Asie; invazně také na Floridě.',
        'funFact': 'Krajta tmavá po spolknutí velké kořisti zvýší metabolismus a několik dní ji tráví v úkrytu.'
    },
    'anolis_carolinensis': {
        'habitat': 'Keře, ploty a kmeny stromů v jihovýchodních státech USA a na Karibských ostrovech.',
        'funFact': 'Samci anolisů rozvěšují sytě červený lalok na krku a mění barvu těla podle nálady i teploty.'
    },
    'haliaeetus_leucocephalus': {
        'habitat': 'Pobřežní lesy, jezera a řeky Severní Ameriky.',
        'funFact': 'Orlové bělohlaví staví obrovská hnízda, která mohou vážit přes tunu a používat je desítky let.'
    },
    'falco_peregrinus': {
        'habitat': 'Útesy, hory a městské mrakodrapy na všech kontinentech kromě Antarktidy.',
        'funFact': 'Sokoli stěhovaví se ve střemhlavém letu řítí na kořist rychlostí přes 320 km/h – jsou nejrychlejšími tvory planety.'
    },
    'aptenodytes_forsteri': {
        'habitat': 'Mořský led a okolní vody Antarktidy.',
        'funFact': 'Tučňáci císařští inkubují vejce na nohou pod záhybem kůže, zatímco samci několik měsíců nejedí.'
    },
    'ara_macao': {
        'habitat': 'Vlhké nížinné lesy Střední a Jižní Ameriky.',
        'funFact': 'Pestrá pera aru arakangy inspirovala mnohé kultury; ptáci si navzájem doživotně udržují pár.'
    },
    'cyanocitta_cristata': {
        'habitat': 'Listnaté lesy, parky a předměstské čtvrti ve východní části Severní Ameriky.',
        'funFact': 'Sojky chocholaté napodobují volání jestřábů jako varovný signál nebo k odehnání konkurence od potravy.'
    },
    'grus_japonensis': {
        'habitat': 'Rašeliniště a říční mokřady severovýchodní Asie.',
        'funFact': 'Páry jeřábů mandžuských si upevňují vztah synchronizovanými tanci a duetovým troubením.'
    },
    'bubo_virginianus': {
        'habitat': 'Lesy, pouště i městské parky napříč Amerikou.',
        'funFact': 'Výr virginský loví i ježky nebo skunky a díky pevným drápům je schopen odnést těžkou kořist.'
    },
    'pelecanus_occidentalis': {
        'habitat': 'Pobřežní laguny, ústí řek a bariérové ostrovy od Pacifiku po Atlantik.',
        'funFact': 'Jako jediný pelikán se střemhlav vrhá z výšky, složí křídla a s otevřeným zobákem proráží hladinu.'
    },
    'balaeniceps_rex': {
        'habitat': 'Papyrusové bažiny a jezerní mokřady východní Afriky.',
        'funFact': 'Jeho zobák ve tvaru dřeváku silně sevře i klínatské ryby a mladé krokodýly.'
    },
    'sagittarius_serpentarius': {
        'habitat': 'Otevřené savany a stepní oblasti subsaharské Afriky.',
        'funFact': 'Dlouhé nohy sekretáře umožňují rychlé rázné kopy, jimiž omráčí hady na zemi.'
    },
    'ramphastos_sulfuratus': {
        'habitat': 'Vlhké nížinné i podhůrské lesy od jižního Mexika po severní Kolumbii.',
        'funFact': 'Duha na zobáku je tvořena lehkou keratinovou voštinou, takže tukan může obratně poskakovat po větvích.'
    },
    'archilochus_colubris': {
        'habitat': 'Lesy a zahrady východní Severní Ameriky; zimuje ve Střední Americe.',
        'funFact': 'Kolibříci rubínohrdlí mávají křídly asi pětapadesátkrát za sekundu a jako jediní ptáci létají pozpátku.'
    },
    'struthio_camelus': {
        'habitat': 'Otevřené savany a polopouště subsaharské Afriky.',
        'funFact': 'Pštros může při běhu překonat rychlost 70 km/h a jeho kopance dokážou zlomit i leví čelist.'
    },
    'casuarius_casuarius': {
        'habitat': 'Husté deštné lesy Nové Guineje a severního Queenslandu.',
        'funFact': 'Kasuar má na vnitřním prstu dýkovitý dráp, který použije, pokud se cítí ohrožen.'
    },
    'pavo_cristatus': {
        'habitat': 'Lesy, zemědělská krajina a vesnice Indie a Srí Lanky.',
        'funFact': 'Samci roztahují duhové ocasy poseté „očima“, aby okouzlili pávice a prokázali své zdraví.'
    },
    'diomedea_exulans': {
        'habitat': 'Jižní oceán a rozsáhlé oblasti mezi subantarktickými ostrovy.',
        'funFact': 'Albatrosi stěhovaví s rozpětím až 3,5 metru dokážou klouzat celé hodiny bez mávnutí křídel.'
    },
    'fratercula_arctica': {
        'habitat': 'Útesy severního Atlantiku od Kanady po Skandinávii.',
        'funFact': 'Papuchalk díky jazykovým ostnům udrží v zobáku i tucet rybek, které donáší mláďatům.'
    },
    'eudocimus_ruber': {
        'habitat': 'Pobřežní mangrovy, bahnité mělčiny a deltová ústí od severní Jižní Ameriky po Karibik.',
        'funFact': 'Hejno šarlatových ibisů vytvoří ve vzduchu V a po západu slunce se vrací na nocoviště v záři karmínové barvy.'
    },
    'bubo_scandiacus': {
        'habitat': 'Tundra a pobřežní zóny arktických oblastí Severní Ameriky, Evropy i Asie.',
        'funFact': 'Hustě opeřené nohy a drápy chrání sovu sněžnou před mrazem i ostrým větrem na otevřené pláni.'
    },
    'buceros_bicornis': {
        'habitat': 'Tropické stálezelené lesy Indie a jihovýchodní Asie.',
        'funFact': 'Dvojzoborožec indický má dutý kostěný přilbovitý výrůstek, kterým při letu vytváří dunivý zvuk.'
    },
    'menura_novaehollandiae': {
        'habitat': 'Vlhké příměstské a horské lesy jihovýchodní Austrálie.',
        'funFact': 'Samec lyrochvosta napodobuje fotoaparáty, motorové pily i zvuk sirén a při námluvách rozvine ocas do tvaru lyry.'
    },
    'corvus_corax': {
        'habitat': 'Hory, lesy, tundry i pouště napříč severní polokoulí.',
        'funFact': 'Krkavci řeší složité úkoly, používají nástroje a pro radost předvádějí letecké akrobatické kousky.'
    },
    'aquila_chrysaetos': {
        'habitat': 'Horské hřebeny, útesy i otevřená vřesoviště Eurasie, Severní Ameriky a severní Afriky.',
        'funFact': 'Monogamní páry znovu staví na stejném hnízdě mnoho let a každou sezónu přidávají další větve.'
    },
    'harpia_harpyja': {
        'habitat': 'Tropické deštné pralesy od jižního Mexika po severní Argentinu.',
        'funFact': 'Drápy harpyje jsou velikostí srovnatelné s drápy medvěda grizzly a dokážou vyrvat opice přímo z koruny stromu.'
    },
    'cygnus_olor': {
        'habitat': 'Jezera, pomalu tekoucí řeky a okrasné rybníky po Evropě i v zavlečených oblastech.',
        'funFact': 'Labutě velké udržují celoživotní páry a energicky brání svoje hnízdiště.'
    },
    'alcedo_atthis': {
        'habitat': 'Čisté potoky, rybníky a říční meandry Evropy, severní Afriky a Asie.',
        'funFact': 'Během lovu zavírá ledňáček průhlednou třetí víčka, aby viděl ostře i pod hladinou.'
    },
    'mycteria_americana': {
        'habitat': 'Lesní mokřady a bažiny jihovýchodních USA, Střední Ameriky a severu Jižní Ameriky.',
        'funFact': 'Čáp se živí pohmatem – jakmile se ryba dotkne otevřeného zobáku, během milisekund ho zaklapne.'
    },
    'turdus_migratorius': {
        'habitat': 'Okraje lesů, městské trávníky a parky po většině Severní Ameriky.',
        'funFact': 'Drozd stěhovavý běží, zastaví se a naklání hlavu, aby zaslechl žížaly; jeho ranní zpěv patří k prvním hlasům jara.'
    },
    'egretta_thula': {
        'habitat': 'Pobřežní močály, mangrovy a sladkovodní mokřady napříč Amerikami.',
        'funFact': 'Lesklé žluté prsty používá k rozvíření vody a zaskočí tak rybky i korýše.'
    },
    'tyto_alba': {
        'habitat': 'Pastviny, zemědělskou krajinu a otevřené lesy na všech kontinentech kromě Antarktidy.',
        'funFact': 'Srdcovitá maska sovy pálené směruje nejtišší zvuky do asymetrických uší, takže slyší i skrytý pohyb hlodavců.'
    }
}

locale_path = Path('data/animals.locale.cs.json')
locale = json.loads(locale_path.read_text(encoding='utf-8'))

for ident, data in translations.items():
    if ident in locale:
        locale[ident]['habitat'] = data['habitat']
        locale[ident]['funFact'] = data['funFact']

locale_path.write_text(json.dumps(locale, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
