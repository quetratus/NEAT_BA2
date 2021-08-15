from game_env import *
import neat
import visualize
import csv
from numpy import *

# Credit zoharehan/AI-Plays-Chrome-Dino-Game

# show score
def show_score(score, penguins):
    highscore_value = font.render("Highscore : " + str(highscore), True, WHITE)
    screen.blit(highscore_value, (10, 10))
    score_value = font.render("Score : " + str(score), True, WHITE)
    screen.blit(score_value, (10, 30))
    score_value = font.render("Gens: " + str(GENERATION - 1), True, WHITE)
    screen.blit(score_value, (10, 50))
    score_value = font.render("Alive: " + str(len(penguins)), True, WHITE)
    screen.blit(score_value, (10, 70))


def draw_window(scrollingBg, penguins, fishes, enemies, score):
    # define elements on screen
    scrollingBg.draw()
    for penguin in penguins:
        penguin.draw(screen)

    for enemy in enemies:
        enemy.draw(screen)
        enemy.move()
    for fish in fishes:
        fish.draw(screen)
        fish.move()

    show_score(score, penguins)


def remove_penguin(index):
    penguins.pop(index)
    ge.pop(index)
    nets.pop(index)


def main(genomes, config):
    global penguins, nets, ge
    global GENERATION
    global highscore
    GENERATION += 1
    gamespeed = 6
    bg_speed = 4
    # scrolling of background to the left
    scrollingBg = Background(-1 * bg_speed)

    # penguins, neural network and genomes
    penguins = []
    nets = []
    ge = []

    # Create list of obstacle class objects
    enemies = [Enemy(gamespeed)]
    fishes = [Fish(45, 25)]

    frame = 0
    score = 0

    # List of Genomes
    # we need the underscore to loop through the indexes of the genomes
    for _, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config) # init the KNN
        nets.append(net) # add the network to the list of networks
        penguin = (Penguin(72, 64))
        penguins.append(penguin) # add penguin to the list of penguins
        genome.fitness = 0  # start with fitness level of 0
        ge.append(genome) # add the genome to the list of genomes

    run = True
    while run and len(penguins):
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        for x, penguin in enumerate(penguins):
            penguin.move()
            ge[x].fitness += 0.01

            # enemy index and fish index is 0
            enemy_ind = 0
            fish_ind = 0
            if len(penguins) > 0:
                # to check which snowman; if penguin passes the first snowman then change index to 1
                if len(enemies) > 1 and penguins[0].rect.x > enemies[0].rect.x + enemies[0].rect.width:
                    enemy_ind = 1
                if len(fishes) > 1 and penguins[0].rect.x > fishes[0].rect.x + fishes[0].rect.width:
                    fish_ind = 1
            else:
                break

            # check for the distance between penguin and the snowman
            # and get the output from the gene (ANN) after feeding necessary inputs
            output = nets[penguins.index(penguin)].activate((
                                                            penguin.rect.y,
                                                             abs(enemies[enemy_ind].rect.x - penguin.rect.x),
                                                             abs(enemies[enemy_ind].rect.y - penguin.rect.y),
                                                             abs(fishes[fish_ind].rect.x - penguin.rect.x),
                                                             abs(fishes[fish_ind].rect.y - penguin.rect.x)
                                                            ))

            # Perform duck or jump according to the ouput
            if output[0] > 0.5:
                penguin.jump()
            if output[1] > 0.5:
                penguin.duck()
            else:
                # penguin is running
                penguin.unduck()

        for fish in fishes:
            for x, penguin in enumerate(penguins):
                if fish.collide(penguin):
                    ge[x].fitness += 0.1
                    score += 5
                    for fish in fishes:
                        fishes.remove(fish)
                        fishes.append(Fish(45, 25))
                elif fish.rect.right <= 0:
                    for fish in fishes:
                        fishes.remove(fish)
                        fishes.append(Fish(45, 25))

        for enemy in enemies:
            enemy.move()
            for x, penguin in enumerate(penguins):
                if enemy.collide(penguin):
                    # Reduce the fitness of that penguin by 1
                    ge[x].fitness -= 1
                    remove_penguin(x)

                if enemy.rect.x <= 0:
                    for enemy in enemies:
                        enemies.remove(enemy)
                        enemies.append(Enemy(gamespeed))
                        score += 1
                        # Increase the fitness of every genome that has survived by 1
                        for g in ge:
                            g.fitness += 1
            enemy.move()

        for penguin in penguins:
            penguin.move()

        # score increases every 1/4 second
        if frame % 10 == 0:
            score += 1

        draw_window(scrollingBg, penguins, fishes, enemies, score)
        scrollingBg.update()
        frame += 1

        if score % 10 == 0:
            row = [GENERATION, score]
            with open("scores_per_generation.csv", 'a') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(row)
            csvfile.close()

        if (len(penguins)<=0) and (score > highscore):
            highscore = score
            row = [GENERATION, score, frame, genome.fitness]
            with open("score_over_iterations.csv", 'a') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(row)
            csvfile.close()

        # if score reaches beyond 500, end the game
        if score > 1000:
            run = False
            row = [GENERATION, score, frame, genome.fitness]
            with open("score_over_1000.csv", 'a') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(row)
            csvfile.close()
            pygame.quit()
            quit()

        pygame.display.update()


def run(config_path):
    global score
    # runs the NEAT algorithm to train the neural network, and sets location for the config file
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    # set up population based on the config file
    p = neat.Population(config)

    # set output for the statistics
    p.add_reporter(neat.StdOutReporter(True))
    statistics = neat.StatisticsReporter()
    p.add_reporter(statistics)

    # call the fitness function and config file for 50 generations
    winner = p.run(main, 50)

    statistics.save()

    p.remove_reporter(statistics)

    # show final statistics
    print('\nBest genome:\n{!s}'.format(winner))

    node_names = {-1: "y-Position Penguin", -2: "distToNextObstable xPosition",
                  -3: "distToNextObstable yPosition", -4: "distToNextBonusItem xPosition", -5: "distToNextBonusItem yPosition",
                  0: 'Jump', 1: 'Duck', 2: 'Unduck', 3: "Nothing"}

    visualize.draw_net(config, winner, True, node_names=node_names)
    visualize.plot_stats(statistics, ylog=False, view=True)
    visualize.plot_species(statistics, view=True)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    fields = ['generation', 'score']
    with open("scores_per_generation.csv", 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(fields)

    fields = ['generation', 'highscore', 'frame', 'fitness']
    with open("score_over_iterations.csv", 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(fields)

    fields = ['generation', 'highscore', 'frame', 'fitness']
    with open("score_over_1000.csv", 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(fields)

    run(config_path)
