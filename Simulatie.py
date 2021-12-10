'''
LET OP!
    DE X EN Y POSITIE OP HET SCHERM WORDT VANAF LINKSBOVEN WORDEN GETELD (NET ZOALS BIJ JAVASCRIPT).
    DIT BETEKENT DAT DE POSITIE, VERSNELLING, SNELHEID ETC. VOOR DE Y WAARDE OMGEKEERD IS.
    OM DE RAKET OP ONS SCHERM NAAR BOVEN TE LATEN GAAN MOETEN DE X EN Y VERSNELLINGEN NEGATIEF ZIJN.

    DE TIJD OP DIT MOMENT IN DE SIMULATIE IS 1:1 EN KAN VERSNELD/VERSLOOMD WORDEN.
    OM DE TIJD SNELLER TE LATEN GAAN: KLIK OP PIJLTJE NAAR RECHTS
    OM DE TIJD SLOMER TE LATEN GAAN: KLIK OP PIJLTJE NAAR LINKS
    OM DE TIJD TE RESETTEN: KLIK OP SPATIE, PIJLTJE NAAR BENEDEN OF PIJLTJE NAAR BOVEN

    OP DIT MOMENT VALT DE RAKET TERUG TIJDENS DE SIMULATIE (IK HEB HET PROBLEEM NOG NIET ECHT BEKEKEN).
    HET KAN ZIJN DAT DE GRAVITATIEVERSNELLING DE RAKET OP DIE HOOGTE OVERMEESTERT OF IETS IN DIE RICHTING.
    OM DIT TE FIXEN: MISS SCHAAL VAN AFSTAND AANPASSEN OF UBERHAUPT JULLIE FORMULE ERIN ZETTEN OM DE VERSNELLING TE BEREKENEN.
'''

# Importeert alle libaries die deze simulatie mogelijk maken.
import sys, pygame, math, os
from pygame.locals import *
import ctypes
from timeit import default_timer as timer

# De variabelen die gebruikt worden in de rest van de code.
width = 1920
height = 1080

# Het scherm inladen
ctypes.windll.user32.SetProcessDPIAware()
pygame.display.set_mode((width, height))
screen = pygame.display.set_mode((width, height), pygame.NOFRAME)

# Standaard acties bij het opstarten.
pygame.init()
pygame.font.init()
pygame.display.set_caption('V-2 Simulatie')

def main():
    clock = pygame.time.Clock()
    fps = 60
    time_factor = 0
    time_scale = math.pow(10, time_factor)
    milliseconds = 0
    delta_time, start, end = 0, 0, 0
    paused = False

    pressed0, pressed1, pressed2 = False, False, False

    font = pygame.font.SysFont('Arial Black', 30)
    background = pygame.transform.scale(pygame.image.load(os.path.join("images", "V2 bg.png")), (width, height))

    distance_scale = 363.6 # Dit is de variabele die bepaalt hoe hoog de raket komt op ons scherm
    gravitational_constant = 6.67384 *math.pow(10, -11)
    mass_earth = 5.972 *math.pow(10, 24) #kg
    radius_earth = 6364864 #m  https://rechneronline.de/earth-radius/ met altitude 52.1 op aarde (rond lanceerplaats) op zeeniveau


    # De Klasse om objecten te kunnen maken, grafisch in te laden en up te daten
    class V2raket:
        def __init__(this, mass, width, height, vx, vy, ax, ay, thrust, burn_time, angle, image):
            this.mass = mass
            this.width = width
            this.height = height
            this.x = 0
            this.y = 0
            this.vx = vx
            this.vy = vy
            this.ax = ax
            this.ay = ay
            this.thrust = thrust
            this.burn_time = burn_time
            this.angle = angle
            this.image = pygame.transform.scale(pygame.image.load(os.path.join("images", image)), (this.width, this.height))

        def calculate(this): # Hier komt alle code wat maar voor 1 keer uitgevoerd moet worden (voor de vlucht, bedoeld voor berekeningen).
            this.x_center = this.width/2
            this.y_center = this.height/2
            this.gravitational_acceleration = (gravitational_constant * mass_earth) / (math.pow(radius_earth, 2))
            this.thrust = this.thrust * this.gravitational_acceleration * 1000

        def render(this): # Hier komt alle code die ervoor zorgt dat er op het scherm getekend of geplakt wordt. Denk hierbij aan de afbeelding van de V-2 die elke keer op een andere positie geplakt moet worden.
            # Op het laatste moment de waardes omzetten naar de waardes voor in de simulatie."+ pixels" is om de raket op de juiste plek te laten beginnen. "+ x/y_center" is om het plaatje in het midden van de raket te plakken.
            this.x_scale = (this.x / distance_scale) + 1715 + this.x_center
            this.y_scale = -(this.y / distance_scale) + 1007 - this.y_center
            screen.blit(pygame.transform.rotate(this.image, this.angle), (int(this.x_scale), int(this.y_scale)))

        def update(this): # Hier komt alle code die de berekeningen en variabelen toepassen om de V-2 op de milisecondes goed te laten lopen.
            # De massa van de raket heeft hier niks mee te maken. Deze valt weg bij het berekenen van de versnelling (ipv van de kracht bij de standaardformule).
            this.gravitational_acceleration = (gravitational_constant * mass_earth) / (math.pow(this.y + radius_earth, 2))

            #this.ax = nog_geen_idee
            if milliseconds < 68000:
                this.mass -= (8800/68) * delta_time * time_scale # 8800
                this.thrust += (5000/68) * delta_time * time_scale * this.gravitational_acceleration
                this.ay = (this.thrust/this.mass) - this.gravitational_acceleration # 264900
            else:
                this.ay = - this.gravitational_acceleration

            # delta_time zorgt ervoor dat het, het aantal keer dat de code opgeroepen wordt, opheft. De tijdschaal is dan 1:1 (delta_time/times_per_second_loop = 1). De time_scale kan aangepast worden op basis van hoe snel je de simulatie wilt laten gaan.
            this.vx += this.ax * delta_time * time_scale
            this.vy += this.ay * delta_time * time_scale
            this.x += this.vx * delta_time * time_scale
            this.y += this.vy * delta_time * time_scale

            this.angle = 0 #2*math.pi*math.atan2(this.vx, -this.vy)  # Zoiets is het om de rotatie te krijgen, maar ik weet niet precies hoe het moet.


    # Maakt het V-2 aan met de beginwaardes
    # V2=V2raket(mass, width, height, vx, vy, ax, ay, thrust, burntime, angle, image)
    V2 = V2raket(12800, 21, 81, 0, 0, -0.05, 0.1, 25, 68, 0, "V-2cut.png")
    V2.calculate()

    start = timer()

    # Dit is loop, deze code is de stam van de code die een aantal keer per seconde uitgevoerd moet worden.
    while True:
        end = timer()

        delta_time = end - start

        start = timer()

        # Reset alle objecten en maakt het scherm "leeg" (anders blijven de geplakt plaatjes van de V-2 van (bijvoorbeeld) een seconde nog geleden staan).
        screen.blit(background, (0,0))

        # Tekent en update de V-2.
        V2.update()
        V2.render()

        # Zet de waardes van de V-2 op het scherm.
        screen.blit(font.render("Tijdschaal: 1:10^" + str(time_factor), False, (255, 255, 255)), (0, 0))
        screen.blit(font.render("Tijd verlopen: " + str(round(milliseconds/1000, 1)) + " s", False, (255, 255, 255)), (0, 50))

        screen.blit(font.render("X: " + str(int(V2.x_scale)), False, (255, 255, 255)), (1650, 0))
        screen.blit(font.render("Y: " + str(int(V2.y_scale)), False, (255, 255, 255)), (1650, 50))
        screen.blit(font.render("Dist.: " + str(round(V2.x/1000, 1)) + " km", False, (255, 255, 255)), (1650, 100))
        screen.blit(font.render("Height: " + str(round(V2.y/1000, 1)) + " km", False, (255, 255, 255)), (1650, 150))
        screen.blit(font.render("Vx: " + str(int(V2.vx)), False, (255, 255, 255)), (1650, 200))
        screen.blit(font.render("Vy: " + str(int(V2.vy)), False, (255, 255, 255)), (1650, 250))
        screen.blit(font.render("AX: " + str(int(V2.ax)), False, (255, 255, 255)), (1650, 300))
        screen.blit(font.render("Ay: " + str(int(V2.ay)), False, (255, 255, 255)), (1650, 350))
        screen.blit(font.render("Ay: " + str(int(V2.mass)), False, (255, 255, 255)), (1650, 400))
        screen.blit(font.render("Ay: " + str(int(V2.thrust)), False, (255, 255, 255)), (1650, 450))

        screen.blit(font.render("dT: " + str(delta_time), False, (255, 255, 255)), (1650, 500))

        # Met de volgende knoppen kan de tijd slomer en sneller gezet worden. Ook kan de tijd stil gezet worden, evenals de simulatie gereset
        # DEEL 1 ZORGT ERVOOR DAT WAARDES MAKKELIJK AAN TE PASSEN ZIJN, JE KAN DE KNOPPPEN NIET INGEDRUKT HOUDEN
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # Zorgt ervoor dat als het programma gesloten wordt, de simulatie daadwerkelijk stopt.
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and pressed0 == False:
                    time_factor -= 0.5
                    pressed0 = True
                elif event.key == pygame.K_RIGHT and pressed1 == False:
                    time_factor += 0.5
                    pressed1 = True
                elif event.key == pygame.K_SPACE and pressed2 == False:
                    if paused == False:
                        paused = True
                    elif paused == True:
                        paused = False
                    pressed2 = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and pressed0:
                    pressed0 = False
                elif event.key == pygame.K_RIGHT and pressed1:
                    pressed1 = False
                elif event.key == pygame.K_SPACE and pressed2:
                    pressed2 = False
        # DEEL 2 IS MINDER PRECIES DAN DEEL 1, MAAR DE KNOPPEN KUNNEN WEL INGEDRUKT GEHOUDEN WORDEN
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            main() # Reset de simulatie
        if keys[pygame.K_UP] and -2 <= time_factor < 5:
            time_factor = 0
        if keys[pygame.K_DOWN] and -2 <= time_factor < 5:
            time_factor = 0

        if paused == False:
            time_scale = math.pow(10, time_factor)
        elif paused == True:
            time_scale = 0

        pygame.display.flip() # Laad elke frame in op het scherm.
        milliseconds += (clock.tick(fps))*time_scale # Maximale frames per seconde (het maximale aantal keer dat de loop doorlopen wordt).
main()