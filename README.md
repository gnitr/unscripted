# Unscripted

* **Description**: a proof-of-concept of an collaborative online virtual world to experiment with unscripted bots
* **Primary** Objective: encourage creation of artificial general intelligent agents (0 prior knowledge about world, no training data, general purpose, 100% algorithmically controlled)
* **Secondary**: Let's see what happens when we let bots live their own life, reproduce, survive, thrive and create their own stories.
* **Focus**: liviness and individual behaviour rather than high level intelligence and optimal actions, life-long and generational evolutions rather than one-shot bots, human-like situations and conditions, psychological, social and behavioural emphasis rather than low-level sensory input processing, an community framework rather than a proprietary algorithm
* **Status**: Development of phase 1 just started (see 'roadmap' section below)

## About me

I have some background in software engineering, a bit in AI and film studies. If anything here inspires you or tickle your interest please feel free to contact me via github. Unfortunately I can only work on this in my spare time. I've had this idea for more than 15 years but never had a chance to do anything practical about it! Read more about [my perspectives on AI](https://github.com/goffer-looney/unscripted/wiki/Personal-Vision-&-Beliefs).

If you borrow anything from here, please be nice and give credit or link back to it. The goal is to promote this particular approach and I'm interested to learn what other similar initiatives look like.

## Why?
Have you ever watched a film, read a book, played an adventure or RPG game and got really immersed into that world but left wanting for more? You enjoyed the quests, the backstories, the characters, the turn of events, ... but you often noticed that it is all scripted. It is a limited construct authored by humans. They let you glimpse at their fabricated world. You only see and experience the narrative paths designed for you. You have limited choices among pre-written dialogues, cut-off scenes. 

Ever wished you could ask questions to anybody in that story, interact your own way and get responses which are their own? Whished you could go on a tangent, digress to something completely different? You could delve into a minor side-story or secondary characters you found more interesting? Wished that world was as limitless and free as reality. Something unscripted. Without plot-holes because characters have a real past, because your story is part of a real, single, coherent history in a fictional world. 

I don't think it is fully possible but I'm convinced we can do better than the dominant fictional models, than what you find in a book, a movie, a game, etc. 

One way to do it is to have other people like you take part in the story, like a massively multiplayer online game. But those can be disappointing because players don't believe in the fictional world; they know it's another leisure activity. They are not there all the time, they won't be there for a lifetime. And they often introduce their own concern from real life into the game.

# What?
A better approach would be a virtual world where characters are played by machines. Just like bots in video games. But the difference is that they are not brainless dummies with scripted behaviour and dialogues. When you land into the game they have been in that world for a long time, eveything you see is the result of their actions. Like us they can have a longer life, they can think independently and they experience pain, pleasure and try to survive. We put them under the same evolutionary conditions as us and see how they can deal with it.

# Implementation

The idea is to build a proof of concept, a basic prototype to see how things work and get inspired or inspire other initiatives. To start the ball rolling. It's won't have fancy visuals and fancy AI, etc. Instead the focus will be on an open platform where world objects and 'bots' can be developed by anyone. It will be very simple but modular and collaboratively extensible.

# That's impossible!

Yeah, despite all the amazing progresses in narrow AI in recent years we are very far away from artificial general intelligence. Common sense, ability to learn from few examples, real emotions, ability to model things in your mind before trying them, multi-skilled agents, knowledge transfer, human-like communication abilities, ... none of that is feasible at the moment. 

So what about this idea of having human-like intelligent bots? Well, let's start with the end and assume this will be possible one day. We then introduce a few key elements to help things happening:
* we provide **a virtual world**: it is a sandbox where anything can happen. Safe for humans and our reality. It will help the bots evolve freely without caring about morally negative consequences within our reality. This offers a standard platform for people to create their own bots;
* **open platform**: bots will be implemented externally by independent teams; as part of this project we only provide example bots but very dumb. Real experts are welcome to step in and create their own intelligent agent on their own machines. They will interract with our world via a web API;
* **zero prior knowledge**: you could create an illusion of smart behaviour by using traditional procedural techniques. But what's the point of having yet another scripted agent that reacts to known world events and communication keywords with mostly predefined actions? So we introduce this crucial rule of having no (or almost no) prior knowledge about the virtual world. They have to learn as much as possible via experience, tradition and observation. If possible the world logic will try to penalise bots that use knowledge embedded by humans. We may also want to apply the same drastic rules to cognitive process: it should be, as much as possible, emergent rather than scripted;
* **evolutionary life**: the bots will be born into the world and may have a long life. We don't expect them to hit the ground running. Moreover they can reproduce, so intelligence can happen via long-term and large quantity of experiences and inter-generational activities. Intelligence can obviously also evolve through regular improvement of the bot algorithms; but that's not the only way. The world will promote survival of the fittest via life-challenging events and competition for resources. Health/survival and a simple model of pain and pleasure will be embedded in the world logic. That should give bots inner drive, practical aims and possibly more subtle psychological processes.

# Architecture

The architecture will be open and modular. Contributors will be able to take control remotely and in real-time of the mind of one or more bots by using the web api.

There will be a very crude web visualisation of a world and the bots so anyone can have an overview of the activity. More advanced and fancy visualisations can be contributed later by using the web api.

Main components:
* **World logic**: a simulated time-space continuum filled with objects with physical laws, interraction rules and mechanism, turn based system for bot actions, ...
* **Non-living object** logic (extensible): e.g.  tree, a chair, and how they interract with bots and other objects
* **Living objects**: i.e. bots
* **Web API** for the bots to communicate with the world and its objects
* **Visualisation** (e.g. a 2D map of the world in a web page), via Web API

# Road map

## Phase 1: Skeleton architecture

* empty world (a 2D square with no non-living objects)
* Web API
* Dumb bot: random walk, nothing else
* 2D grid rendering in a web page

## Phase 2: Interaction with objects

* create a few world objects and implement the way bots can interract with them

## Phase 3: Needs for resources and survival

* introduce resources that the bots can consume (water, food, shelter, temperature, ...)
* they experience sensations when they need or misuse resources (hunger, cold, ...)
* bots can die due to unfulfilled needs 
* new bots replace dead ones

## Phase 4: Reproduction and inheritence

* bots can reproduce
* bots can inherit from parents

## Phase 5 and beyond: TBC
* communication
* ...

# Derived projects

If successfull, the initial project can lead to many interesting research strands, well beyond Computer Science, AI or video games:
* experiments with unguided AI life evolution
* a new type of Turing test (comparing humans ands bots ability to solve virtual world challenges)
* a way for AI researchers to experiment with their own algorithms, and compare their achievements with others
* a safe sandbox for future real-world intelligences
* emergence of non-human controlled narratives
* stimulate philosophical, psychological and ethical questions
* playground for evolutionary, non-human behaviours
* emergent agent-agent communication
* virtual-world history
* what if? Let a world develop by itself then after a long period of tiem we tweak it (modify bots, events, world) to see what happens; We could also create time travel for bots and other time and space disruptions. What if? We seed a world with a setting close to what happened in human history to see how bots would solve a problem.
* study of agent-human interactions
* video game NPCs that are not dumb or predictable 
* ...

# Open questions

There are many open questions. How to build a simple but working model that allows bots to come up with more advanced psychology? What communication should be like? How human-like do we want the bots to be? How can we technically enforce rules that will promote general artificial intelligence? ...

Some of those questions are very challenging or have many valid answers. We can't explore them all but they are a fascinating aspect of the project and hopefully even a basic, working implementation will provide many occasions to investigate them and try new ideas.
