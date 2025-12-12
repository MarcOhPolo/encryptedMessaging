# Development Log
Project: <Encrypted Messaging>  
Author: <Marco Silva>  
Start Date: <2025-9-23>

---

## Overview
A development log documenting the progress of building a Python-based messaging system using sockets. This log captures decisions, challenges, design changes, and lessons learned throughout the project.

The purpose of this project is to practice my programming skils, learn about encryption schemes (strengths and weaknesses) but also a deeper understanding of networking. To this end I will not be using any guides, or information about how messaging protocols work or other networking details (except encryption schemes but I will detail where I learn things from and what for). The point to use my own intuition to try to "reinvent the wheel" so to speak, and in that process hopefully learn as much as possible, and by then end *hopefully* have a working, albeit a very limited, messaging service of my own!

---

## How to Read This Log
Each entry includes:
- **Date**
- **Description of what was done**
- **Optional concept notes to describe anything I thought particularly interesting**

---

## Entries

A quick note before the start of the entries: I started this project a while ago but due to other things taking my time I put this on standby, but I am finally back to it! :D

### 2025-11-22 (Saturday):

With multithreading on the client, a shared resource of somekind is necessary between the listener and UI threads, I opted to make a new object using the python Queue library since it's generally more thread safe than other data structures. My demand for thread safety isn't very great at most the client will have 4-5 threads (each for a new p2p connection) which makes it unlikely race conditions to be violated. A few nice emergent features of making EventBus have come up; now I can keep all the handling of encoded data out of client.py, which makes the code much more readable. Also much less repeated code! I spent most of the day transfering and tweaking the decoding logic from client.py to EventBus. 

TLDR: Now client.py is much more about just handling the UI, listening and decoding information from the server has become much more simplified using EventBus.py.

Concept Note: I’ve noticed that keeping the client focused on handling simple Python primitives while moving all packet-processing logic into a separate object has made the code far easier to work with and has greatly improved debuggability. When both the client logic and the EventBus functionality were merged into a single file, identifying the source of a problem was much harder. Now, with each component having a clearer purpose, it’s much easier to isolate issues and reason about the flow of data.

After doing some research, I found that this idea aligns with the software engineering principle known as Separation of Concerns. I’ve encountered the concept before—even if I didn’t know the name at the time—but this is the most illuminating and hands-on experience I’ve had with it. It’s exactly the kind of insight I was hoping to gain from this project, so it’s great to see that I’m already learning these architectural principles early on.

### 2025-11-23 (Sunday):

Since adding the EventBus feature, I can finally return to expanding (or in some cases, re-implementing lol) several features. Some of these existed before, but I removed them after revisiting the code and nearly imploding at how messy it looked. There’s still progress to be made on the server side especially, but things are definitely moving in the right direction.

I’m getting close to finishing the P2P scheme, the last major step is sending messages to the address the client receives, plus applying encryption, which I can handle later. Next on the agenda is switching to JSON-based communication. Up until now, I’ve been sending plain UTF-8 encoded strings as a prototype. That worked initially, but I’m now hitting the limits of what a simple string-based approach can handle.

For example, I now need to send tuples (containing the peer’s IP and port), and encoding/decoding those through the pipeline of
tuple → string → encoded and then decoded → string → tuple
is extremely clunky and error-prone. JSON solves this cleanly, and it will also let me add future features like timestamps or message metadata without fighting the format. I always knew this transition would happen eventually, and it shouldn’t take long to implement… (famous last words lol).

### 2025-11-24
Realised massive problem with asychronous events which needs to be fixed later on.
I need to redesign a lot of the way the client intreracts with the terminal; the current method is causing problems such as:
Inputs are interrupted by incoming connection requests. The root cause is that I don't have a cohesive vision for how the UI should actually look like. I want to stay within the terminal for the minial approach and don't want to bother with GUI libraries, however it is very limiting. I might try to make certain segments of the terminal that change live for incoming connection requests and an area just for the user to type commands, or I can have everything in demand from a user such that interuptions to the user only appear once they make a explicit request like: /userlist - then they can do /request [user]. This might make more sense than having a main menu which is the main problem.
---

### 2025-12-10
Before finishing the new command system, I am making changes to how eventbus works. Right now it's a singular queue where every kind of request goes into, however I am running into a problem where due to having asynchoronous events such as: p2p connection requests, when I do Eventbus.get() the queue might pop a p2p connection request instead of the thing intended. Right now I can't include a search for a specific op code which makes the process difficult, I've decided to implement Eventbus with multiple queues inside to make it easier

---

## Architecture or Concept Notes (Optional)
Use this section to jot down any important design thoughts that don’t fit neatly into a daily entry:

-  
-  

---

## Reflections (Optional but recommended)
A place to summarize what you have learned recently or after major milestones.

- What went well:  
  -  

- What didn’t go well:  
  -  

- What I learned:  
  -  

- What I want to explore next:  
  -  

