# Unscripted

* **Description**: a proof-of-concept of a collaborative online virtual world to experiment with unscripted bots
* **Primary Objective**: encourage creation of artificial general intelligent agents (0 prior knowledge about world, no training data, general purpose, 100% algorithmically controlled)
* **Secondary**: Let's see what happens when we let bots live their own life, reproduce, survive, thrive and create their own stories.
* **Focus**: 
  * unscripted behaviour rather than high level intelligence and optimal solution solving
  * life-long and generational evolutions rather than adult-born bots
  * human-like situations, psychological, social and behavioural emphasis rather than low-level sensory input processing
  * emphasis on the development of the mind rather than detailed body and physical interactions with world
  * build an open framework rather than a proprietary algorithm
* **Status**: Phase 1 is complete. Phase 2 planned for November 2017 (see 'roadmap' section below)

Copyright (c) 2017 Artilligence Ltd, UK

[Background](https://github.com/gnitr/unscripted/wiki/Motivations-&-Background)

[About us](https://github.com/gnitr/unscripted/wiki/About-Us)

[Implementation Details](https://github.com/gnitr/unscripted/wiki/Implementation-Details)

# Road map

## 0.1: Set up architecture (completed Oct 2017, to be documented)

* empty world (a 2D square with bots only)
* 2D grid rendering in a web page
* basic world engine running in the background
* dumb bot: acts randomly
* run bot as a background process on client side
* Web API for distributed architecture

## 0.2: A new mortal mind (starting late Nov 2017)

* create a simple test world with a few bots and shared resources
* bots can consume resources
* bots can die of old age or shortage of resources
* new bots replace dead ones
* create a very basic but working model of a bot mind (initially takes random actions but model can become purposeful)

## 0.3: Genetic transmission

* genome = a serialised mind
* species = a type of model for a mind and its serialisation format
* bots have genders, same species bots can breed
* birth = a deserialisation of a recombination of two serialised minds

Those simple ingredients should be enough trigger the evolutionary process. This is when things starts to become really interesting and move in many directions.

## 0.4: Public Demo

* keep revising and optimising the system until we can see the emergence and transmission of behaviours
* add complexity to the world (other situations, resources, things)
* upload video of the system with explanations
* possibly set up a live site
* report findings and discuss the choices made; how they compare with animal evolution; what works and what doesn't; where can we go from here

Other ideas:
* support for individual memorisation of events
* possibility to transport and trade items
* bots can alter the world
* bots can create new things
* bots can communicate (using emergent language expressed in ascii strings)

Questions:
* human genome and brain doesn't contain memories; but the bot genome could potentially be a complete snapshot of a mind; should it be avoided, if so how, if not what are the implications?
* can bot evolution really emerge from the genetic transmission and survival?
* how does the bot mind update itself during its life if there are no predefined feedback or reward system from the world? Everything is neutral; can the bots build their reward system from it?
* could we create a self-modifying mind? if so, how much can be changed and how can it be changed?
