import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        if len(self.cells) == self.count and self.count > 0:
            return self.cells.copy()
        return set()

    def known_safes(self):
        if self.count == 0:
            return self.cells.copy()
        return set()

    def mark_mine(self, cell):
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):
        self.height = height
        self.width = width
        self.moves_made = set()
        self.mines = set()
        self.safes = set()
        self.knowledge = []

    def mark_mine(self, cell):
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        self.moves_made.add(cell)
        self.mark_safe(cell)

        # Get neighbors and create a new sentence
        neighbors = self.get_neighbors(cell)
        unknown_neighbors = neighbors - self.safes - self.mines
        new_sentence = Sentence(unknown_neighbors, count - len(neighbors & self.mines))

        if len(new_sentence.cells) > 0:
            self.knowledge.append(new_sentence)

        self.update_knowledge()

    def update_knowledge(self):
        max_iterations = 100  # Set a maximum number of iterations
        for _ in range(max_iterations):
            changes_made = False

            # Check for new mines or safes in existing sentences
            for sentence in self.knowledge.copy():
                new_mines = sentence.known_mines()
                new_safes = sentence.known_safes()
            
                for mine in new_mines:
                    if mine not in self.mines:
                        self.mark_mine(mine)
                        changes_made = True
                for safe in new_safes:
                    if safe not in self.safes:
                        self.mark_safe(safe)
                        changes_made = True

            # Remove empty sentences
            self.knowledge = [s for s in self.knowledge if len(s.cells) > 0]

            # Infer new sentences
            for i, s1 in enumerate(self.knowledge):
                for s2 in self.knowledge[i + 1:]:
                    inferred = self.infer_from_sentences(s1, s2)
                    if inferred and inferred not in self.knowledge:
                        self.knowledge.append(inferred)
                        changes_made = True

            # Check for cells that appear in all sentences
            all_cells = set.intersection(*[s.cells for s in self.knowledge]) if self.knowledge else set()
            for cell in all_cells:
                if all(s.count == len(s.cells) for s in self.knowledge if cell in s.cells):
                    if cell not in self.mines:
                        self.mark_mine(cell)
                        changes_made = True
                elif all(s.count == 0 for s in self.knowledge if cell in s.cells):
                    if cell not in self.safes:
                        self.mark_safe(cell)
                        changes_made = True

            if not changes_made:
                break  # Exit the loop if no changes were made

    def infer_from_sentences(self, s1, s2):
        if s1.cells.issubset(s2.cells):
            new_cells = s2.cells - s1.cells
            new_count = s2.count - s1.count
            return Sentence(new_cells, new_count)
        elif s2.cells.issubset(s1.cells):
            new_cells = s1.cells - s2.cells
            new_count = s1.count - s2.count
            return Sentence(new_cells, new_count)
        return None

    def make_safe_move(self):
        safe_moves = self.safes - self.moves_made
        return random.choice(list(safe_moves)) if safe_moves else None

    def make_random_move(self):
        all_moves = set((i, j) for i in range(self.height) for j in range(self.width))
        possible_moves = list(all_moves - self.moves_made - self.mines)
        return random.choice(possible_moves) if possible_moves else None

    def get_neighbors(self, cell):
        i, j = cell
        neighbors = set()
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if di == 0 and dj == 0:
                    continue
                ni, nj = i + di, j + dj
                if 0 <= ni < self.height and 0 <= nj < self.width:
                    neighbors.add((ni, nj))
        return neighbors

