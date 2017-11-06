# Unscripted

* **Description**: a proof-of-concept of a collaborative online virtual world to experiment with unscripted bots
* **Primary Objective**: encourage creation of artificial general intelligent agents (0 prior knowledge about world, no training data, general purpose, 100% algorithmically controlled)
* **Secondary**: Let's see what happens when we let bots live their own life, reproduce, survive, thrive and create their own stories.
* **Focus**: 
  * unscripted behaviour rather than high level intelligence and optimal solution solving, 
  * life-long and generational evolutions rather than adult-born bots, 
  * human-like situations, psychological, social and behavioural emphasis rather than low-level sensory input processing, 
  * build an open framework rather than a proprietary algorithm
* **Status**: Development of phase 1 just started (see 'roadmap' section below)

Copyright (c) 2017 Artilligence Ltd 

[Background](https://github.com/gnitr/unscripted/wiki/Motivations-&-Background)

[About us](https://github.com/gnitr/unscripted/wiki/About-Us)

[Implementation Details](https://github.com/gnitr/unscripted/wiki/Implementation-Details)

# Road map

## 0.1: Skeleton architecture (started Oct 2017, complete, to be documented)

* empty world (a 2D square with bots only)
* 2D grid rendering in a web page
* basic world engine running in the background
* dumb bot: random walk, nothing else
* run bot as a background process
* Web API and distributed architecture

## 0.2: Interaction with objects

* create a few world objects and implement the way bots can interract with them
* bots are still dumb (random actions or scripted in order to test the framework)

## 0.3: Needs for resources and survival

* introduce resources that the bots can consume (water, food, shelter, temperature, ...)
* they experience sensations when they need or misuse resources (hunger, cold, ...)
* bots can die due to unfulfilled needs 
* new bots replace dead ones

## 0.4: Reproduction and inheritence

* bots can reproduce
* bots can inherit from parents
* bots should define the genetic material of their mind (i.e. enough information to build a new mind, info can be mutated and combined with others)

## 0.5 and beyond: TBC
* communication
* ...

