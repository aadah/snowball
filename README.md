# Snowball Algorithm

(Note: This program requires non-code resources that can be locally accessed.
Preprocessing/building the database takes a while. This README will be updated
with what resources are needed and where to get them, plus a recommended
way to organize the resource directory.)

Based on [this paper](http://www.mathcs.emory.edu/~eugene/papers/dl00.pdf).

## How to run

1. Go to `~/resources/snowball/`

2. Make a directory `<some_name>`

3. Go to `<some_name>/`

4. Create a file called 'seeds'. Contents are as follows:
   - 1st line:	 A name for your relation (e.g. located_in). No whitespace.
   - 2nd line:	 Subject tag and object tag. Must be separated by at least one whitespace character. See stanford corenlp to know which tags are allowed. Make sure they are capitalized.
   - 3rd line onwards: Pair of tokens where whitespace is replaced by one underscore and tokens are separated by whitespace.

5. Open `config/config.py` in project directory. Replace `<some_name>` in
   `SNOWBALL_SEEDS_FILE`  with the name you chose.

6. The other `SNOWBALL_*` parameters can be changed, but be careful. Increasing
   iterations will make the program run more slowly per iteration.

7. Start elasticstart. Go to `~/resources/elasticsearch-1.7.0/bin/` and run:

   	 ./elasticsearch

   It is good to do this in a screen session.

8. Return to project directory and run the following to start Snowball: `python main/main.py`

9. You can monitor the system by running: `tailf ~/resources/logs/snowball.log`

10. Tuples will be in `~/resources/snowball/<some_name>/tuples`. Each line
    is a Tuple object that can be evaluated in python.
    For a cleaner read of the results, run:

       	 python classes/read.py > out

    The results will be in `out`. Each line is of the form `SUBJ OBJ`.
