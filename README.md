# Unscripted

* **Description**: a proof-of-concept of a collaborative online virtual world to experiment with unscripted bots
* **Primary Objective**: encourage creation of artificial general intelligent agents (0 prior knowledge about world, no training data, general purpose, 100% algorithmically controlled)
* **Secondary**: Let's see what happens when we let bots live their own life, reproduce, survive, thrive and create their own stories.
* **Focus**: 
  * unscripted behaviour rather than high level intelligence and optimal solution solving
  * life-long and generational evolutions rather than adult-born bots
  * human-like situations, psychological, social and behavioural emphasis rather than low-level sensory input processing
  * emphasis on the development of the mind rather than detailed body and physical interactions with world
  * building an open framework rather than a proprietary algorithm
  * hoping to provoke new questions and reactions rather than building a fixed world
  * bold, unrealistic, naive and playful approach rather than cautious, formal, all-knowing and critical
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

