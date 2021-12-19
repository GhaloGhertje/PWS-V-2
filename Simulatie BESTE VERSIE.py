'''
LET OP!
    Het tijdsverloop van de simulatie is 1:1 en kan versneld worden. De simulatie kan ook gereset worden, op pauze gezet worden en de baan kan aan en uit gezet worden.

    Om de tijd sneller te laten gaan: klik op pijltje naar rechts.
    Om de tijd slomer te laten gaan: klik op pijltje naar links.
    Om de tijd te resetten: klik op pijltje naar beneden of pijltje naar boven.
    Om de simulatie te resetten: klik op "R".
    Om de simulatie op pauze te zetten: klik op "Spatie".
    Om de baan van de V-2 aan en uit te zetten: klik op "T".

TO DO
    Versnelling positief en negatief tov de raket.
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
explosion = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(os.path.join("images", "Explosion.png")), (100, 100)), -3.5)


# Alles wat veranderd in de simulatie staat in deze functie. Zodat deze functie opnieuw opgeroepen kan worden en alles gereset wordt.
def main():
    # Maakt een nieuwe oppervlakte aan waarop de baan van de V-2 permanent op geprojecteerd kan worden.
    screen_layer = pygame.Surface((width, height), pygame.SRCALPHA)

    # Print de 90 km op de nieuwe oppervlakte.
    screen_layer.blit(font.render("90 km", False, (255, 255, 255)), (1810, 420))

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

    # De constanten die de meters omzetten naar pixels.
    distance_scale_x = 200
    distance_scale_y = 167.5

    # De variabelen/constanten waarmee de zwaartekracht berekend wordt.
    gravitational_constant = 6.67384 *math.pow(10, -11)
    mass_earth = 5.972 *math.pow(10, 24) #kg
    radius_earth = 6364864 #m  https://rechneronline.de/earth-radius/ met altitude 52.1 op aarde (rond lanceerplaats) op zeeniveau.



    # De Klasse om objecten te kunnen maken, grafisch in te laden en up te daten.
    class V2raket:
        def __init__(this, mass, width, height, vx, vy, ax, ay, thrust, burn_time, angle, image, thrust_image, render_rocket, thrust_switch):
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
            this.thrust_image = pygame.transform.scale(pygame.image.load(os.path.join("images", thrust_image)), (this.width, this.height + 70))
            this.render_rocket = render_rocket
            this.thrust_switch = thrust_switch

        def calculate(this): # Hier komt alle code wat maar voor 1 keer uitgevoerd moet worden (voor de vlucht, bedoeld voor berekeningen).
            this.x_center = this.width/2
            this.y_center = this.height/2
            this.gravitational_acceleration = (gravitational_constant * mass_earth) / (math.pow(radius_earth, 2))
            this.thrust = this.thrust * this.gravitational_acceleration * 1000
            this.acceleration = -this.gravitational_acceleration
            this.velocity = 0


        def render(this): # Hier komt alle code die ervoor zorgt dat er op het scherm getekend of geplakt wordt. Denk hierbij aan de afbeelding van de V-2 die elke keer op een andere positie geplakt moet worden.        
            if this.thrust_switch:
                # Zorgt ervoor dat het middelpunt van de draai van het lange plaatje afgestemd wordt op de graden. 35 is hierbij het verschil van het midden tussen het lange en het korte plaatje.
                this.delta_x_center_component = math.sin(math.radians(this.angle)) * 35
                this.delta_y_center_component = math.cos(math.radians(this.angle)) * 35
                
                # Op het laatste moment de waardes omzetten naar de waardes voor in de simulatie."+ pixels" is om de raket op de juiste plek te laten beginnen. "+ x/y_center" is om het plaatje in het midden van de raket te plakken.
                this.x_scale = (this.x / distance_scale_x) + 1736 + this.delta_x_center_component
                this.y_scale = -(this.y / distance_scale_y) + 1007 + this.delta_y_center_component

                this.rotated_image = pygame.transform.rotate(this.thrust_image, this.angle)
                this.rect = this.rotated_image.get_rect(center = (this.x_scale, this.y_scale))

                screen.blit(this.rotated_image, this.rect)

                pygame.draw.circle(screen_layer, (0,0,255), (this.x_scale - this.delta_x_center_component, this.y_scale - this.delta_y_center_component), 4)
                if this.y <= 10000:
                    pygame.draw.circle(screen_layer, (0,0,255), (this.x_scale, this.y_scale), 4)
            
            elif this.render_rocket and not this.thrust_switch:
                # Op het laatste moment de waardes omzetten naar de waardes voor in de simulatie."+ pixels" is om de raket op de juiste plek te laten beginnen. "+ x/y_center" is om het plaatje in het midden van de raket te plakken.
                this.x_scale = (this.x / distance_scale_x) + 1736
                this.y_scale = -(this.y / distance_scale_y) + 1007

                this.rotated_image = pygame.transform.rotate(this.image, this.angle)
                this.rect = this.rotated_image.get_rect(center = (this.x_scale, this.y_scale))
                
                screen.blit(this.rotated_image, this.rect)

                pygame.draw.circle(screen_layer, (0,0,255), (this.x_scale, this.y_scale), 4)
            
            else:
                screen.blit(explosion, (this.x_scale -75, 960))


            pygame.draw.line(screen_layer, (255,255,255), (0, -90000 / distance_scale_y + 1007), (1920, -90000 / distance_scale_y + 1007))


        def update(this): # Hier komt alle code die de berekeningen en variabelen toepassen om de V-2 op de milisecondes goed te laten lopen.
            # De massa van de raket heeft hier niks mee te maken. Deze valt weg bij het berekenen van de versnelling (ipv van de kracht bij de standaardformule).
            this.gravitational_acceleration = (gravitational_constant * mass_earth) / (math.pow(this.y + radius_earth, 2))
            
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
            elif this.y > -3000:
                this.thrust_switch = False
                this.thrust = 0
                this.ay = - this.gravitational_acceleration - (math.cos(math.atan2(this.vy, this.vx)) * this.air_resistance) / this.mass
                this.ax = - (math.sin(math.atan2(this.vy, this.vx)) * this.air_resistance) / this.mass
            
            # De raket is ingeslagen en de snelheid en versnelling staat nu op 0
            else:
                this.ay = 0
                this.ax = 0
                this.vx = 0
                this.vy = 0
                this.render_rocket = False

                return False

            # delta_time zorgt ervoor, dat het aantal keer dat de code opgeroepen wordt, wordt opgeheven. De tijdschaal is dan 1:1 (delta_time/times_per_second_loop = 1). De time_scale kan aangepast worden op basis van hoe snel je de simulatie wilt laten gaan.
            this.vx += this.ax * delta_time * time_scale
            this.vy += this.ay * delta_time * time_scale
            this.x += this.vx * delta_time * time_scale
            this.y += this.vy * delta_time * time_scale

            this.angle = math.degrees(math.atan2(-this.vx, this.vy)) # Haalt de rotatie van de raket uit de snelheidsvector. Door middel van de inverse tangus.
            return True


    # Maakt het V-2 aan met de beginwaardes
    # V2=V2raket(mass, width, height, vx, vy, ax, ay, thrust, burntime, angle, image, thrust_image, render_rocket, thrust_switch)
    V2 = V2raket(12800, 21, 81, 0, 0, 0, 0, 25, 68, 0, "V-2.png", "V-2thrust.png", render_rocket, thrust_switch)
    V2.calculate()

    time_scale = 0
    start = timer()



    # Dit is loop, deze code is de stam van de code die een aantal keer per seconde uitgevoerd moet worden.
    while True:
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
            screen.blit(font.render("Baan: aan", False, (255, 255, 255)), (1530, 0))
        else:
            screen.blit(font.render("Baan: uit", False, (255, 255, 255)), (1530, 0))

        # Zet de V-2 op het scherm.
        V2.render()

        # Zet de waardes van de V-2 op het scherm.
        if time_factor == 0:
            screen.blit(font.render("Tijdschaal: 1:1", False, (255, 255, 255)), (1530, 50))
        elif time_factor == 0.5:
            screen.blit(font.render("Tijdschaal: 1:10", False, (255, 255, 255)), (1530, 50))
            screen.blit(superscript.render("0.5", False, (255, 255, 255)), (1790, 47))
        elif time_factor == 1:
            screen.blit(font.render("Tijdschaal: 1:10", False, (255, 255, 255)), (1530, 50))
        elif time_factor == 1.5:
            screen.blit(font.render("Tijdschaal: 1:10", False, (255, 255, 255)), (1530, 50))
            screen.blit(superscript.render("1.5", False, (255, 255, 255)), (1790, 47))
        else:
            screen.blit(font.render("Tijdschaal: 1:100", False, (255, 255, 255)), (1530, 50))

        screen.blit(font.render("Verstreken tijd: " + str(round(seconds_past, 1)) + " s", False, (255, 255, 255)), (1530, 100))

        screen.blit(font.render("Afstand: " + str(abs(round(V2.x/1000, 1))) + " km", False, (255, 255, 255)), (10, 0))
        screen.blit(font.render("Hoogte: " + str(round(V2.y/1000, 1)) + " km", False, (255, 255, 255)), (10, 50))
        screen.blit(font.render("Snelheid: " + str(round(V2.velocity/1000, 1)) + " km/s`¹", False, (255, 255, 255)), (10, 100))
        screen.blit(font.render("Versnelling: " + str(round(V2.acceleration, 1)) + " m/s²", False, (255, 255, 255)), (10, 150))
        screen.blit(font.render("Massa: " + str(round(V2.mass/1000, 1)) + " ton", False, (255, 255, 255)), (10, 200))
        screen.blit(font.render("Stuwkracht: " + str(round(V2.thrust/1000, 1)) + " kN", False, (255, 255, 255)), (10, 250))

        # Met de volgende knoppen kan de tijd slomer en sneller gezet worden. Ook kan de tijd stil gezet worden, evenals de simulatie gereset.
        # DEEL 1 zorgt voor knoppen die niet ingedrukt gehouden kunnen worden.
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # Zorgt ervoor dat als het programma gesloten wordt, de simulatie daadwerkelijk stopt.
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and not pressed0 and 0 < time_factor <= 2:
                    time_factor -= 0.5
                    pressed0 = True
                elif event.key == pygame.K_RIGHT and  not pressed1 and 0 <= time_factor < 2:
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
        if keys[pygame.K_UP] and 0 <= time_factor < 2:
            time_factor = 0
        if keys[pygame.K_DOWN] and 0 <= time_factor < 2:
            time_factor = 0

        if paused:
            time_scale = 0
        else:
            time_scale = math.pow(10, time_factor)

        pygame.display.flip() # Laad elke frame in op het scherm.
        clock.tick((base_ticks*time_scale)) # Maximale frames per seconde (het maximale aantal keer dat de loop doorlopen wordt).


# Roept de functie hierboven op.
main()