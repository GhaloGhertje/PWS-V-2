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

# 3 constanten die gebruikt worden in de rest van de code.
width = 1920
height = 1080
fps = 60

# Het scherm inladen
ctypes.windll.user32.SetProcessDPIAware()
pygame.display.set_mode((width, height))
screen = pygame.display.set_mode((width, height), pygame.NOFRAME)

# Standaard acties bij het opstarten.
pygame.init()
pygame.font.init()
pygame.display.set_caption('V-2 Simulatie')

font = pygame.font.SysFont('Arial Black', 30)
background = pygame.image.load(os.path.join("images", "V2 bg.png")).convert()

def main():
    # De variabelen die gebruikt worden in de rest van de code.
    clock = pygame.time.Clock()
    time_factor = 0
    time_scale = math.pow(10, time_factor)
    seconds_past = 0
    delta_time, start, end = 0, 0, 0
    paused = True

    pressed0, pressed1, pressed2 = False, False, False
    distance_scale_x = 200
    distance_scale_y = 181.5 # Dit is de variabele die bepaalt hoe hoog de raket komt op ons scherm
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
            this.x_scale = (this.x / distance_scale_x) + 1715 + this.x_center
            this.y_scale = -(this.y / distance_scale_y) + 1007 - this.y_center
            screen.blit(pygame.transform.rotate(this.image, this.angle), (int(this.x_scale), int(this.y_scale)))

            pygame.draw.line(screen, (255,255,255), (0 / distance_scale_x + 1715 + this.x_center, 0), (0 / distance_scale_x + 1715 + this.x_center, 1080))
            pygame.draw.line(screen, (255,255,255), (-320000 / distance_scale_x + 1715 + this.x_center, 0), (-320000 / distance_scale_x + 1715 + this.x_center, 1080))
            pygame.draw.line(screen, (255,255,255), (0, -90000 / distance_scale_y + 1007 - this.y_center), (1920, -90000 / distance_scale_y + 1007 - this.y_center))


        def update(this): # Hier komt alle code die de berekeningen en variabelen toepassen om de V-2 op de milisecondes goed te laten lopen.
            # De massa van de raket heeft hier niks mee te maken. Deze valt weg bij het berekenen van de versnelling (ipv van de kracht bij de standaardformule).
            this.gravitational_acceleration = (gravitational_constant * mass_earth) / (math.pow(this.y + radius_earth, 2))

            this.velocity = math.sqrt((this.vx**2) + (this.vy**2))
            this.air_resistance = (((1.4477 * math.e**(-0.0001 * this.y) * 0.10 * 2.14) / 2) * (this.velocity**2)) # 0.0000252, 0.1, 0.76
            #luchtdichtheid rond 60-70 km en rond de 0-40 km in kg/m^3  - https://www.engineeringtoolbox.com/standard-atmosphere-d_604.html
            #ongeveer de drag coefficient van de neus van de V-2 (ogive). deze neuzen hebben een Cd van tussen de 0.05 en 0.23. https://www.astro.rug.nl/~hoek/geometric-aerodynamics.pdf
            #straal van de raket zonder vinnen is 0.823 m dus de opp is 2,14
            
            # Alleen versnelling omhoog
            if seconds_past < 38.5:
                this.mass -= (8800/68) * delta_time * time_scale # 8800
                this.thrust += (5000/68) * delta_time * time_scale * this.gravitational_acceleration
                this.resultant_force = this.thrust - (this.air_resistance)

                this.ay = (this.resultant_force/this.mass) - this.gravitational_acceleration # 264900

            # Tussen deze tijden beweegt de V-2 onder een hoek van ongeveer 45 graden, waardoor de thrust in de richting vd x en y ongeveer even groot zijn.
            elif seconds_past >= 38.5 and seconds_past < 68:
                this.mass -= (8800/68) * delta_time * time_scale # 8800
                this.thrust += ((5000/68) * delta_time * time_scale * this.gravitational_acceleration)
                this.resultant_force = this.thrust - this.air_resistance

                this.x_resultant_force = this.resultant_force * math.sin(math.radians(55))
                this.y_resultant_force = this.resultant_force * math.cos(math.radians(55))
                #this.y_thrust = this.resultant_force * math.sqrt(1/2) # Wortel(1/2) is afgeleid uit pythagoras als de rechte zijden aan elkaar gelijk zijn
                #this.x_thrust = this.resultant_force * math.sqrt(1/2)

                this.ax = -(this.x_resultant_force/this.mass)
                this.ay = (this.y_resultant_force/this.mass) - this.gravitational_acceleration

            elif this.y > 0:
                this.ay = - this.gravitational_acceleration - (math.cos(math.atan2(this.vy, this.vx)) * this.air_resistance) / this.mass
                this.ax = - (math.sin(math.atan2(this.vy, this.vx)) * this.air_resistance) / this.mass
            
            else:
                this.ay = 0
                this.ax = 0
                this.vx = 0
                this.vy = 0

            # delta_time zorgt ervoor dat het, het aantal keer dat de code opgeroepen wordt, opheft. De tijdschaal is dan 1:1 (delta_time/times_per_second_loop = 1). De time_scale kan aangepast worden op basis van hoe snel je de simulatie wilt laten gaan.
            this.vx += this.ax * delta_time * time_scale
            this.vy += this.ay * delta_time * time_scale
            this.x += this.vx * delta_time * time_scale
            this.y += this.vy * delta_time * time_scale

            this.angle = math.degrees(math.atan2(-this.vx, this.vy))  # Zoiets is het om de rotatie te krijgen, maar ik weet niet precies hoe het moet.


    # Maakt het V-2 aan met de beginwaardes
    # V2=V2raket(mass, width, height, vx, vy, ax, ay, thrust, burntime, angle, image)
    V2 = V2raket(12800, 21, 81, 0, 0, 0, 0, 25, 68, 0, "V-2cut.png")
    V2.calculate()

    time_scale = 0

    start = timer()

    # Dit is loop, deze code is de stam van de code die een aantal keer per seconde uitgevoerd moet worden.
    while True:
        end = timer()
        delta_time = end - start

        # Update waardes van de V-2.
        V2.update()
        
        # Timer om de tijd te meten hoe lang de computer doet om de loop uit te voeren.
        start = timer()

        # Het optellen van de secondes (die voorbij zijn) voor de timer
        seconds_past += delta_time * time_scale

        # Reset alle objecten en maakt het scherm "leeg" (anders blijven de geplakt plaatjes van de V-2 van (bijvoorbeeld) een seconde nog geleden staan).
        screen.blit(background, (0,0))

        # Zet de V-2 op het scherm.
        V2.render()

        # Zet de waardes van de V-2 op het scherm.
        screen.blit(font.render("Tijdschaal: 1:10^" + str(time_factor), False, (255, 255, 255)), (0, 0))
        screen.blit(font.render("Tijd verlopen: " + str(round(seconds_past, 1)) + " s", False, (255, 255, 255)), (0, 50))

        screen.blit(font.render("X: " + str(int(V2.x_scale)), False, (255, 255, 255)), (1650, 0))
        screen.blit(font.render("Y: " + str(int(V2.y_scale)), False, (255, 255, 255)), (1650, 50))
        screen.blit(font.render("Dist.: " + str(round(V2.x/1000, 1)) + " km", False, (255, 255, 255)), (1650, 100))
        screen.blit(font.render("Height: " + str(round(V2.y/1000, 1)) + " km", False, (255, 255, 255)), (1650, 150))
        screen.blit(font.render("Vx: " + str(round(V2.vx, 1)), False, (255, 255, 255)), (1650, 200))
        screen.blit(font.render("Vy: " + str(round(V2.vy, 1)), False, (255, 255, 255)), (1650, 250))
        screen.blit(font.render("AX: " + str(round(V2.ax, 1)), False, (255, 255, 255)), (1650, 300))
        screen.blit(font.render("Ay: " + str(round(V2.ay, 1)), False, (255, 255, 255)), (1650, 350))
        screen.blit(font.render("Mass: " + str(round(V2.mass, 1)), False, (255, 255, 255)), (1650, 400))
        screen.blit(font.render("Thr: " + str(round(V2.thrust, 1)), False, (255, 255, 255)), (1650, 450))
        screen.blit(font.render("dT: " + str(delta_time), False, (255, 255, 255)), (1650, 500))

        # Met de volgende knoppen kan de tijd slomer en sneller gezet worden. Ook kan de tijd stil gezet worden, evenals de simulatie gereset
        # DEEL 1 ZORGT ERVOOR DAT WAARDES MAKKELIJK AAN TE PASSEN ZIJN, JE KAN DE KNOPPPEN NIET INGEDRUKT HOUDEN
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # Zorgt ervoor dat als het programma gesloten wordt, de simulatie daadwerkelijk stopt.
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and pressed0 == False and -2 < time_factor <= 3:
                    time_factor -= 0.5
                    pressed0 = True
                elif event.key == pygame.K_RIGHT and pressed1 == False and -2 <= time_factor < 3:
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
        if keys[pygame.K_UP] and -2 <= time_factor < 3:
            time_factor = 0
        if keys[pygame.K_DOWN] and -2 <= time_factor < 3:
            time_factor = 0

        if paused == False:
            time_scale = math.pow(10, time_factor)
        elif paused == True:
            time_scale = 0

        pygame.display.flip() # Laad elke frame in op het scherm.
        clock.tick(fps) # Maximale frames per seconde (het maximale aantal keer dat de loop doorlopen wordt).

        
main()
