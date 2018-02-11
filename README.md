# Unscripted

* **Description**: a naive proof-of-concept for a collaborative online virtual world to experiment with unscripted bots
* **Primary Objective**: experiment with of adaptive, artificial human-like agents (0 prior knowledge about world, no training data, general purpose, 100% algorithmically controlled); a sort of artificial general intelligence
* **Secondary**: Let's see what happens when we let bots live their own life, reproduce, survive, thrive and create their own stories.
* **Managing expecations**: **Although the ideas and aims are ambitious this prototype is extremely low-key, minimalistic and rudimentary**. You've got to use your imagination, look at the potential rather than what can be actually achieved with this code. Don't forget: the human brain is one of nature's finest masterpieces but it had very modest beginning millions of years ago; that's my starting point! 
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
* **Status**: Version 0.4 is complete. Next phase planned for March 2018 (see 'roadmap' section below)
* **Demo**: Demo video will come once I see a form of adaptation emerging

Copyright (c) 2017 Artilligence Ltd, UK

[Run it on your machine](https://github.com/gnitr/unscripted/wiki/Installation)

[Implementation Details](https://github.com/gnitr/unscripted/wiki/Implementation-Details)

[Background](https://github.com/gnitr/unscripted/wiki/Motivations-&-Background)

[About us](https://github.com/gnitr/unscripted/wiki/About-Us)

# Screenshot

Be warned, unless you use your imagination it looks pretty underwhelming...

<img src="https://github.com/gnitr/unscripted/blob/master/doc/unscripted-world-0.2.png?raw=true" height="300">

That's 10mx10m world with 10 bots and 2 wells.

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

## 0.3: Optimisations (completed Jan 2018)

* add a backend system to manage collection of things: mongodb, in-memory (pymemdb) (done)
* make the client and server work on separate computer (done)
* try websockets communication instead of http requests (done)
* simple tester to run continuous simulation of a small population and measure performance (done)
* try different configurations (pypy, python 3, different wsgi servers) (done)
* optimisations of the server-side framework to cope with large number of actions (in PROGRESS)

This stage is necessary as I realised that the engine on the server-side is extremely slow. We want the bots to live many times faster than in real time otherwise it will take years to see an emerence of adaptation. Read the discussion about [the speed of virtual life in the Wiki](https://github.com/gnitr/unscripted/wiki/The-Speed-of-Life-&-Learning).

## 0.4: Update the visualisation (completed Feb 2018)
* repair the web based visualisation of the world so it works with websocket server instead of the http server

## 0.5: Adaptive Mind (starting Feb/March 2018)

* create a very basic but working model of a bot mind, possibly neural net
* introduce a basic mechanism for allowing adaptation

## 0.6: Genetic transmission

* genome = a serialised mind
* species = a type of model for a mind and its serialisation format
* bots have genders, same species bots can breed
* birth = a deserialisation of a recombination of two serialised minds

Those simple ingredients should be enough trigger the evolutionary process. This is when things starts to become really interesting and move in many directions.

## 0.7: Public Demo

* keep revising and optimising the system until we can see the emergence and transmission of behaviours
* add complexity to the world (other situations, resources, things)
* upload video of the system with explanations
* possibly set up a live site
* report findings and discuss the choices made; how they compare with animal evolution; what works and what doesn't; where can we go from here

