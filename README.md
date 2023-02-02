# Date Pairing Algorithm
## What is this
This is a fully automated tool that uses information about participants and their preferences to optimally match them with another person that they are compatible with. 

This repository contains the implementation of the algorithm, as an extendible framework that allows for easy customization of the algorithm's parameters. Notably, it performs parsing of the input, performs the matching, and outputs the results in a human-readable format. The matching can be customised in a variety of ways, as described below.


## How to use
This is not meant to be a cli tool, but rather a framework that can be used to implement a cli tool if needed. The main.py file contains an example of how to use the algorithm.

```python
pip install -r requirements.txt
python3 main.py
```
*Tested on Python Python 3.9.0*

This will execute the pairing on the example input file and output the results to the console.


## How to customize
The algorithm can be customized in a variety of ways. The following sections describe the different ways in which the algorithm can be customized.

### Parsing input
To ingest more information about a participant from the input file, add extra fields in Person.build() method.

### Constraints
There are two types of constraints, hard and soft. Hard constraints are constraints that must be satisfied for a pairing to be valid. Soft constraints are constraints that are preferred, but not required.

Hard constraints are defined in the Person.is_pairable() method and soft constraints are defined in the Person.is_pairing_preferred() method. To add either, customise the methods to include the new constraints. A few constraints are already implemented as examples.

### Scoring
The optimality of the solution after the constraints have been satisfied is determined by the score of the pairing between each of the participants. The score between two participants are defined by the Person.compatibility_score() method. To modify how the score is calculated, customise this method to use a different scoring function. Currently, a cosine similarity between the matrices of the participants' is used.

Another key parameter is the config.PENALTY_MULTIPLIER parameter used to penalise violations of soft constraints. See config.py for more information.

### Logging
Once the problem has been solved, MatchMaker.log_matches() is executed using the results of the matching. This method can be customised to log the results in a different way. Currently, the results are logged to the console. Consider extending this method to log the results to a file.

## How does it work??
Mostly magic, with a bit of linear programming.
