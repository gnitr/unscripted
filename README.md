# Unscripted

* **Description**: a naive proof-of-concept for a collaborative online virtual world to experiment with unscripted bots
* **Primary Objective**: experiment with of adaptive, artificial human-like agents (0 prior knowledge about world, no training data, general purpose, 100% algorithmically controlled); a sort of artificial general intelligence
* **Secondary**: Let's see what happens when we let bots live their own life, reproduce, survive, thrive and create their own stories.
* **Focus**: 
  * unscripted behaviour rather than high level intelligence and optimal solution solving
  * life-long and generational evolutions rather than adult-born bots
  * human-like situations, psychological, social and behavioural emphasis rather than low-level sensory input processing
  * emphasis on the development of the mind rather than detailed body and physical interactions with world
  * building an open framework rather than a single AI algorithm
  * hoping to provoke new questions and reactions rather than building a fixed world
  * bold, unrealistic, naive and playful approach rather than cautious, formal, all-knowing and critical
  * wider reflexion about artificial and human life rather than a purely technical project
* **This is NOT**: it's NOT a chat bot! Think P-NPC (a playing non-playing-character). A world where NPCs are the heros.
* **Status**: Phase 2 is complete. Phase 3 planned for November 2017 (see 'roadmap' section below)
* **Demo**: Demo screenshots & video will come once I see a form of adaptation

Copyright (c) 2017 Artilligence Ltd, UK

[Run it on your machine](https://github.com/gnitr/unscripted/wiki/Installation)

[Implementation Details](https://github.com/gnitr/unscripted/wiki/Implementation-Details)

[Background](https://github.com/gnitr/unscripted/wiki/Motivations-&-Background)

[About us](https://github.com/gnitr/unscripted/wiki/About-Us)

# Road map

## 0.1: Set up architecture (completed Oct 2017, to be documented)

* empty world (a 2D square with bots only)
* 2D grid rendering in a web page
* basic world engine running in the background
* dumb bot: acts randomly
* run bot as a background process on client side
* Web API for distributed architecture

## 0.2: Birth of a mortal mind (completed Nov 2017)

* create a simple test world with a few bots and shared resources
* bots can consume resources
* bots can die of 'old age' or shortage of resources
* new bots replace dead ones
* bots still chose actions randomly

## 0.3: Attempts at adaptation (starting Nov 2017)

* create a very basic but working model of a bot mind, possibly neural net
* introduce a basic mechanism for allowing adaptation
* some level of optimisations

## 0.4: Genetic transmission

* genome = a serialised mind
* species = a type of model for a mind and its serialisation format
* bots have genders, same species bots can breed
* birth = a deserialisation of a recombination of two serialised minds

Those simple ingredients should be enough trigger the evolutionary process. This is when things starts to become really interesting and move in many directions.

## 0.5: Public Demo

* keep revising and optimising the system until we can see the emergence and transmission of behaviours
* add complexity to the world (other situations, resources, things)
* upload video of the system with explanations
* possibly set up a live site
* report findings and discuss the choices made; how they compare with animal evolution; what works and what doesn't; where can we go from here

