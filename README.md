# Counting Strategies Simulator

This is a Streamlit web application designed to perform various combinatorics calculations. It provides a user-friendly interface for solving complex counting problems, making it a useful tool for students, educators, and professionals dealing with discrete mathematics and probability.

## Features

The simulator is organized into several tabs, each dedicated to a specific type of counting problem:

*   **Permutations and Combinations (nPr, nCr):** Calculate the number of ways to choose and arrange a subset of items from a larger set.
*   **Inclusion-Exclusion Principle:** Determine the size of the union of multiple sets by accounting for their intersections.
*   **Team Selection with Constraints:** Form a team of a specific size from various groups with constraints on the number of members from each group (minimum, exact, or at most).
*   **Arrangements with Forbidden Adjacency:** Count the number of permutations where certain pairs of items are not allowed to be adjacent to each other.
*   **Scheduling Assignments:** Calculate the number of ways to assign a group of people to a set of slots, given capacity constraints and fixed pre-assignments.

## Installation

To run this application locally, you need to have Python installed. You can then install the necessary dependencies using pip:

```bash
pip install -r requirements.txt
```

## Usage

Once the dependencies are installed, you can run the Streamlit application with the following command:

```bash
streamlit run streamlit_app.py
```

This will start a local web server and open the application in your default web browser. You can then navigate through the different tabs to use the various calculators.
