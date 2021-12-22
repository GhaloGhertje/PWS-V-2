'''
PWS Simulatie V-2

GEMAAKT DOOR:
Ingmar Spaans
Sven Wijnen
Koen van der Horst


LET OP!
    Het tijdsverloop van de simulatie is 1:1 en kan versneld worden. De simulatie kan ook gereset worden, op pauze gezet worden en de baan kan aan en uit gezet worden.

    Om de tijd sneller te laten gaan: klik op pijltje naar rechts.
    Om de tijd slomer te laten gaan: klik op pijltje naar links.
    Om de tijd te resetten: klik op pijltje naar beneden of pijltje naar boven.
    Om de simulatie te resetten: klik op "R".
    Om de simulatie op pauze te zetten: klik op "Spatie".
    Om de baan van de V-2 aan en uit te zetten: klik op "T".
'''

# Importeert alle libaries die deze simulatie mogelijk maken.
import sys, pygame, math, os, ctypes
from pygame.locals import *
from timeit import default_timer as timer


# 3 constanten die gebruikt worden in de rest van de code.
width = 1920
height = 1080
base_ticks = 10


# Het scherm inladen.
ctypes.windll.user32.SetProcessDPIAware() # Zorgt ervoor dat het scherm niet vervormd op een aantal soorten computers.
screen = pygame.display.set_mode((width, height), pygame.NOFRAME)


# Standaard acties bij het opstarten.
pygame.init()
pygame.font.init()
pygame.display.set_caption('V-2 Simulatie')

font = pygame.font.SysFont('Arial Black', 30)
superscript = pygame.font.SysFont('Arial Black', 18)
background = pygame.image.load(os.path.join("images", "V-2 bg.png")).convert()
launch_location_background = pygame.image.load(os.path.join("images", "Launch location bg.png"))

# De constanten die de meters omzetten naar pixels.
distance_scale_x = 200
shift_x = 1736
distance_scale_y = 158
shift_y = 1043 #1045 #989
white = (255,255,255)


# Alles wat veranderd in de simulatie staat in deze functie. Zodat deze functie opnieuw opgeroepen kan worden en alles gereset wordt.
def main():
    # Maakt een nieuwe oppervlakte aan waarop de baan van de V-2 permanent op geprojecteerd kan worden.
    screen_layer = pygame.Surface((width, height), pygame.SRCALPHA)

    # Print de km strepen op de nieuwe oppervlakte.
    layer = 0
    while layer <= 100:
        screen_layer.blit(font.render(str(layer) + " km", False, white), (1790,(-layer*1000 / distance_scale_y) + shift_y - 40))
        pygame.draw.line(screen_layer, white, (0, (-layer*1000 / distance_scale_y) + shift_y), (1920, (-layer*1000 / distance_scale_y) + shift_y))
        layer += 10

    # De variabelen die met tijd hebben te maken in de code.
    clock = pygame.time.Clock()
    time_factor = 0
    time_scale = math.pow(10, time_factor)
    seconds_past = 0
    delta_time, start, end = 0, 0, 0
    paused = True

    # Variabelen die gebruikt worden voor de status van de V-2 en voor de knoppen op het toetsenbord.
    show_trajectory = False
    render_rocket, thrust_switch = True, True
    pressed0, pressed1, pressed2, pressed3 = False, False, False, False

    # De variabelen/constanten waarmee de zwaartekracht berekend wordt.
    gravitational_constant = 6.67384 *math.pow(10, -11)
    mass_earth = 5.972 *math.pow(10, 24) #kg
    radius_earth = 6364864 #m  https://rechneronline.de/earth-radius/ met altitude 52.1 op aarde (rond lanceerplaats) op zeeniveau.



    # De Klasse om objecten te kunnen maken, grafisch in te laden en up te daten.
    class V2raket:
        # Maakt alle beginwaardes van de V-2 aan.
        def __init__(this, mass, width, height, thrust, burn_time, angle, image, thrust_image, render_rocket, thrust_switch):
            this.mass = mass
            this.width = width
            this.height = height
            this.x = 0
            this.y = 0
            this.vx = 0
            this.vy = 0
            this.ax = 0
            this.ay = 0
            this.thrust = thrust
            this.burn_time = burn_time
            this.angle = angle
            this.image = pygame.transform.scale(pygame.image.load(os.path.join("images", image)), (this.width, this.height))
            this.thrust_image = pygame.transform.scale(pygame.image.load(os.path.join("images", thrust_image)), (this.width, this.height))
            this.explosion_image = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(os.path.join("images", "Explosion.png")), (100,100)), -3.5)
            this.explosion_x_position = 0
            this.render_rocket = render_rocket
            this.thrust_switch = thrust_switch
            this.velocity = 0

        # Hier komt alle code wat maar voor 1 keer uitgevoerd moet worden (voor de vlucht, bedoeld voor berekeningen).
        def calculate(this):
            # Bepaalt midden van het plaatje van de V-2.
            this.x_center = this.width/2
            this.y_center = this.height/2
            # Bepaalt de gravitatieversnelling op het eerste punt om de stuwkracht en de versnelling van de raket aan het begin te bepalen.
            this.gravitational_acceleration = (gravitational_constant * mass_earth) / (math.pow(radius_earth, 2))
            this.thrust = this.thrust * this.gravitational_acceleration * 1000
            this.acceleration = -this.gravitational_acceleration

        # Hier komt alle code die ervoor zorgt dat er op het scherm getekend of geplakt wordt. 
        # Denk hierbij aan de afbeelding van de V-2 die elke keer op een andere positie geplakt moet worden.
        def render(this):
            # Deze code zet de berekende hoogte in meters om naar pixels in het scherm. "distance_scale" is de schaal van meter naar pixels 
            # en shift is de verschuiving vanaf linksboven van het scherm om het op de goede positie op het scherm te zetten.
            this.x_scale = (this.x / distance_scale_x) + shift_x
            this.y_scale = -(this.y / distance_scale_y) + shift_y
            
            # Het plaatje met de straal achter de motor wordt hier ingeladen als de motor aan staat.
            if this.thrust_switch:                
                this.rotated_image = pygame.transform.rotate(this.thrust_image, this.angle)
                this.rect = this.rotated_image.get_rect(center = (this.x_scale, this.y_scale))

                screen.blit(this.rotated_image, this.rect)
            
            # Wanneer de motor uit staat
            else:
                # Laat de raket in.
                if this.render_rocket:
                    this.rotated_image = pygame.transform.rotate(this.image, this.angle)
                    this.rect = this.rotated_image.get_rect(center = (this.x_scale, this.y_scale))
                    screen.blit(this.rotated_image, this.rect)
                
                # Als de raket niet meer ingeladen moet worden, laat dan de explosie in.
                else:
                    # Zet de inslaglocatie permanent vast
                    if this.explosion_x_position == 0:
                        this.explosion_x_position = this.x_scale - 95
                    screen.blit(this.explosion_image, (this.explosion_x_position, 960))

            # Tekent elke keer dat deze regel geroepen wordt, een cirkel op het scherm.
            # Deze blijft staan op de laag die aan en uit gezet kan worden.
            pygame.draw.circle(screen_layer, (0,0,255), (this.x_scale, this.y_scale), 4)


        def update(this): # Hier komt alle code die de berekeningen en variabelen toepassen om de V-2 op de milisecondes goed te laten lopen.
            # De massa van de raket heeft hier niks mee te maken. Deze valt weg bij het berekenen van de versnelling (ipv van de kracht bij de standaardformule).
            this.gravitational_acceleration = (gravitational_constant * mass_earth) / (math.pow(this.y + radius_earth, 2))
            
            # Berekening van de totale snelheid en versnelling.
            this.old_velocity = this.velocity
            this.velocity = math.sqrt((this.vx**2) + (this.vy**2))
            this.delta_velocity = this.velocity - this.old_velocity
            this.acceleration = this.delta_velocity * time_scale

            this.air_resistance = (((1.4477 * math.e**(-0.0001 * this.y) * 0.10 * 2.14) / 2) * (this.velocity**2)) # 0.0000252, 0.1, 0.76
            # De luchtdichtheid rond 60-70 km en rond de 0-40 km in kg/m^3  - https://www.engineeringtoolbox.com/standard-atmosphere-d_604.html
            # Ongeveer de drag coefficient van de neus van de V-2 (ogive). deze neuzen hebben een Cd van tussen de 0.05 en 0.23. https://www.astro.rug.nl/~hoek/geometric-aerodynamics.pdf
            # De straal van de raket zonder vinnen is 0.823 m dus het opp is 2,14
            

            # De periode waarin alleen een versnelling recht omhoog plaatsvindt.
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

                this.ax = -(this.x_resultant_force/this.mass)
                this.ay = (this.y_resultant_force/this.mass) - this.gravitational_acceleration

            # Tot op welke hoogte de V-2 zichtbaar is in de simulatie nadat er geen stuwkracht meer aanwezig is.
            elif this.y > 0:
                this.thrust_switch = False
                this.thrust = 0
                this.ay = - this.gravitational_acceleration - (math.cos(math.atan2(this.vy, this.vx)) * this.air_resistance) / this.mass
                this.ax = - (math.sin(math.atan2(this.vy, this.vx)) * this.air_resistance) / this.mass
                # Zet op deze hoogte het plaatje van de raket uit. Bij de inslag van de raket klopt het plaatje niet meer in verhouding tot de inslagplek.
                if this.y < 6000:
                    this.render_rocket = False
            
            # De raket is ingeslagen en de snelheid en versnelling staat nu op 0.
            else:
                this.ay = 0
                this.ax = 0
                this.vx = 0
                this.vy = 0

                return False

            # delta_time zorgt ervoor, dat het aantal keer dat de code opgeroepen wordt, wordt opgeheven. De tijdschaal is dan 1:1 (delta_time/times_per_second_loop = 1). De time_scale kan aangepast worden op basis van hoe snel je de simulatie wilt laten gaan.
            this.vx += this.ax * delta_time * time_scale
            this.vy += this.ay * delta_time * time_scale
            this.x += this.vx * delta_time * time_scale
            this.y += this.vy * delta_time * time_scale

            # Haalt de rotatie van de raket uit de snelheidsvector. Door middel van de inverse tangus.
            this.angle = math.degrees(math.atan2(-this.vx, this.vy))
            return True


    # Maakt het V-2 aan met de beginwaardes
    # V2=V2raket(mass, width, height, thrust, burntime, angle, image, thrust_image, render_rocket, thrust_switch)
    V2 = V2raket(12800, 21, 151, 25, 68, 0, "V-2.png", "V-2thrust.png", render_rocket, thrust_switch)
    V2.calculate()

    # Zet de simulatie "stil" aan het begin.
    time_scale = 0
    
    # Neemt het begin van de timer op om de eerste delta_time waarde accurater te maken en de start variabele aan te maken.
    start = timer()

    # Dit is loop, deze code is de stam van de code die een aantal keer per seconde uitgevoerd moet worden.
    while True:
        # Eindigt de timer en bepaalt het verschil in tijd tussen de eerste en de laatste timer.
        end = timer()
        delta_time = end - start
        
        # Update waardes van de V-2 en stopt de simulatie als de V-2 zijn eindpunt heeft bereikt.
        if V2.update() == False:
            paused = True

        # Timer om de tijd te meten hoe lang de computer doet om de loop uit te voeren.
        start = timer()

        # Het optellen van de secondes (die voorbij zijn) voor de timer.
        seconds_past += delta_time * time_scale

        # Alles wat op het scherm geprojecteerd wordt staat hieronder
        # Reset alle objecten en maakt het scherm "leeg" (anders blijven de geplakt plaatjes van de V-2 van (bijvoorbeeld) een seconde nog geleden staan).
        screen.blit(background, (0,0))

        # Zet de transparante laag op het scherm voor de baan van de V-2, als de gebruiker dit aan heeft staan.
        if show_trajectory:
            screen.blit(screen_layer, (0,0))
            screen.blit(font.render("Grafiek: aan", False, white), (1530,0))
        else:
            screen.blit(font.render("Grafiek: uit", False, white), (1530,0))

        # Zet de V-2 op het scherm.
        V2.render()
        
        # Zet een plaatje over de V-2 heen op de opstijglocatie. Hierdoor gaat de witte straal uit de V-2 niet zichtbaar door de grond heen.
        screen.blit(launch_location_background, (1727,1043))

        # WAARDES OP SCHERM
            # Tijdschaal
        screen.blit(font.render("Tijdschaal: 1:10", False, (255,255, 255)), (1530,50))
        screen.blit(superscript.render(str(time_factor), False, white), (1790,47))
            # Verstreken tijd
        screen.blit(font.render("Verstreken tijd: " + str(round(seconds_past, 1)) + " s", False, white), (1530,100))
            # Afstand
        screen.blit(font.render("Afstand: " + str(abs(round(V2.x/1000, 1))) + " km", False, white), (10,0))
            # Hoogte
        screen.blit(font.render("Hoogte: " + str(round(V2.y/1000, 1)) + " km", False, white), (10,50))
            # Snelheid
        screen.blit(font.render("Snelheid: " + str(round(V2.velocity/1000, 1)) + " km/s", False, white), (10,100))
            # Versnelling
        screen.blit(font.render("Versnelling: " + str(round(V2.acceleration, 1)) + " m/s²", False, white), (10,150))
            # Massa
        screen.blit(font.render("Massa: " + str(round(V2.mass/1000, 1)) + " ton", False, white), (10,200))
            # Stuwkracht
        screen.blit(font.render("Stuwkracht: " + str(round(V2.thrust/1000, 1)) + " kN", False, white), (10,250))

        # Met de volgende knoppen kan de tijd slomer en sneller gezet worden. Ook kan de tijd stil gezet worden, evenals de simulatie gereset.
        # DEEL 1 zorgt voor knoppen die niet ingedrukt gehouden kunnen worden.
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # Zorgt ervoor dat als het programma gesloten wordt, de simulatie daadwerkelijk stopt.
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and not pressed0 and 0 < time_factor <= 1.5:
                    time_factor -= 0.5
                    pressed0 = True
                elif event.key == pygame.K_RIGHT and  not pressed1 and 0 <= time_factor < 1.5:
                    time_factor += 0.5
                    pressed1 = True
                elif event.key == pygame.K_SPACE and not pressed2:
                    paused = not paused
                    pressed2 = True
                elif event.key == pygame.K_t and not pressed3:
                    show_trajectory = not show_trajectory
                    pressed3 = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and pressed0:
                    pressed0 = False
                elif event.key == pygame.K_RIGHT and pressed1:
                    pressed1 = False
                elif event.key == pygame.K_SPACE and pressed2:
                    pressed2 = False
                elif event.key == pygame.K_t and pressed3:
                    pressed3 = False
        
        # DEEL 2 is minder precies, maar de knoppen kunnen wel ingedrukt gehouden worden
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            main() # Reset de simulatie.
        if keys[pygame.K_UP] and 0 <= time_factor < 1.5:
            time_factor = 0
        if keys[pygame.K_DOWN] and 0 <= time_factor < 1.5:
            time_factor = 0

        if paused:
            time_scale = 0
        else:
            time_scale = math.pow(10, time_factor)

        pygame.display.flip() # Laad elke frame in op het scherm.
        clock.tick((base_ticks*time_scale)) # Maximale frames per seconde (het maximale aantal keer dat de loop doorlopen wordt).


# Roept de functie hierboven op.
main()