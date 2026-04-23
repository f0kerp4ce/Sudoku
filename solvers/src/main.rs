use std::{fs, iter::Skip};

#[derive(Debug, Clone)]
struct Sudoku {
    board: [u8; 81], // regular, contains correct solution after bruteforce
    tboard: [u8; 81], // column major stored
    bboard: [u8; 81], // box major stored

    notes: [u16; 81],
    tnotes: [u16; 81],
    bnotes: [u16; 81],

}
// box major: (boxes & inside boxes)
// 0 1 2
// 3 4 5
// 6 7 8

impl Sudoku {
    fn read_from_path(&mut self) {
        let contents = fs::read_to_string("example.txt")
            .expect("Should have been able to read the file");
        let vec: Vec<u8>= contents
            .chars()
            .map(|c| {
                match c {
                    '.' => 0,
                    '1' ..= '9' => c.to_digit(10).unwrap_or(0) as u8,
                    _ => 0,
                }
            }).take(81).collect();

        self.board = vec.try_into().expect("file had less than 81 elements");

        // update other boards
        for i in 0..9 {
            for j in 0..9 {
                self.tboard[j*9+i] = self.board[i*9 + j];
                self.bboard[(i/3)*27 + j%3 + (i%3)*3 + (j/3)*9] = self.board[i*9 + j];
            }
        }
        self.init_notes();
    }

    fn init_notes(&mut self) {
        self.notes = [1022; 81];
        self.tnotes = [1022; 81];
        self.bnotes = [1022; 81];

        for i in 0..9 {
            for j in 0..9 {
                let curr = self.board[i*9 + j];
                if curr == 0 {continue}
                let mask = !(1u16 << curr); // e.g. curr = 3  =>  mask = 0b..11110111
                let box_idx: usize = (i*3)%9 + (i/3)*27 + (j%3) +(j/3)*9;// 0..9
                // update notes for:
                for k in 0..9 {
                    // for row i
                    self.notes[9*i + k] &= mask;
                    self.tnotes[9*j + k] &= mask; // transposed
                    let box_row_idx = (i*3)%9 + (i/3)*27 + (k%3) + (j/3)*9;
                    self.bnotes[box_row_idx] &= mask; // box layout; 3 per column are adjacent; 
                    // for column j
                    self.notes[9*k + j] &= mask;
                    self.tnotes[9*k + i] &= mask;
                    let box_col_idx = (k*3)%9 + (k/3)*27 + (j%3) + (j/3)*9;
                    self.bnotes[box_col_idx] &= mask;
                    // for box ´box_idx´
                    self.notes[9*(i/3 + k/3)*3 + (j/3)*3 + k%3] &= mask;
                    self.tnotes[9*(j/3 + k/3)*3 + (i/3)*3 + k%3] &= mask;
                    self.bnotes[box_idx + k] &= mask;
                }
            }
        }
    }

    fn solve(&mut self) -> bool {
        while (!self.check()) {
            if self.obvious_single() {continue}
            if self.hidden_singles() {continue}

            // else bruteforce
            return self.bruteforce();
        }
        self.check()
    }

    fn check(&self) -> bool {
        return !self.notes.iter().any(|&field| field != 0);
    }

    fn bruteforce(&mut self) -> bool {
        // go through every field, check possibilities and 
        // pick field with the least number of possibilities
        let mut nposs = 10;
        let mut lp_pos = 10000;

        for i in 0..81 {
            let curr = self.notes[i];
            if curr.count_ones() < nposs {
                nposs = curr.count_ones();
                lp_pos = i;
            }
        }
        if nposs == 0 || nposs == 10 {return false}
        let mut curr = self.notes[lp_pos];
        while curr != 0 {
            let test_n = curr.trailing_zeros();
            let mut s = self.clone(); // deep copy, we can keep all the data except for the field we change
            s.set(lp_pos/9, lp_pos%9, test_n as u8);
            if s.solve() {
                self.board = s.board;
                return true;
            } // solve recursively
            // decrement current
            curr &= (curr-1);
        }
        
        
        false
    }

    fn obvious_single(&mut self) -> bool {
        for i in 0..9 {
            let row = self.get_notes_row(i);
            let col = self.get_notes_col(i);
            let block = self.get_notes_box(i);
            
            // check if there is only one possibility
            for j in 0..9 {
                if row[j].count_ones() == 1 {
                    self.set(i, j, row[j].trailing_zeros() as u8);
                    return true;
                }
                else if col[j].count_ones() == 1 {
                    self.set(j, i, col[j].trailing_zeros() as u8);
                    return true;
                }
                else if block[j].count_ones() == 1 {
                    // 'i' is block number; 'j' is position inside block
                    self.set((i/3)*27 + j/3, (i%3)*9 + j%3, block[j].trailing_zeros() as u8);
                    return true;
                }
            }
        }
        false // no obvious single exists
    }

    fn hidden_singles(&mut self) -> bool {
        for i in 0..9 {
            let row = self.get_notes_row(i);
            let col = self.get_notes_col(i);
            let block = self.get_notes_box(i);
            // array [u16; 9] where appearance in field i is 1 for each field, number
            
            // check if there is only one possibility for a number
            let mut row_counts = [0u16; 9];
            let mut col_counts = [0u16; 9];
            let mut block_counts = [0u16; 9];

            for n in 1..10 {
                // count occurences of 'n'
                let mask = 1<<n;
                for j in 0..9 {
                    row_counts[n] += (row[j] & mask) >> n;
                    col_counts[n] += (col[j] & mask) >> n;
                    block_counts[n] += (block[n] & mask) >> n;
                }
                // check if there is a number with only one occurence
                if row_counts[n] == 1 {
                    // find which field is the hidden single
                    for j in 0..9 {
                        if row[j] & mask != 0 {
                            self.set(i, j, row[n].trailing_zeros() as u8);
                            return true;
                        }
                    }
                }
                if col_counts[n] == 1 {
                    for j in 0..9 {
                        if col[j] & mask != 0 {
                            self.set(j, i, col[j].trailing_zeros() as u8);
                            return true;
                        }
                    }
                }
                if block_counts[n] == 1 {
                    for j in 0..9 {
                        if block[j] & mask != 0 {
                            // i is block number, j is number within block
                            self.set((i/3)*27 + j/3, (i%3)*9 + j%3, block[n].trailing_zeros() as u8);
                            return true;
                        }
                    }
                }
                // n is not a hidden single
            }
            // go to next row/col/block
        }
        false // no hidden single exists
    }

    fn set(&mut self, i: usize, j: usize, v: u8) {
        self.board[i*9 + j] = v;
        self.tboard[j*9 + i] = v;
        let box_idx: usize = (i*3)%9 + (i/3)*27 + (j%3) +(j/3)*9;// 0..9
        self.bboard[box_idx] = v;

        // update notes
        let mask = !(1u16 << v); // e.g. v = 3  =>  mask = 0b..11110111

        for k in 0..9 {
            // for row i
            self.notes[9*i + k] &= mask;
            self.tnotes[9*j + k] &= mask; // transposed
            let box_row_idx = (i*3)%9 + (i/3)*27 + (k%3) + (j/3)*9;
            self.bnotes[box_row_idx] &= mask; // box layout; 3 per column are adjacent; 
            // for column j
            self.notes[9*k + j] &= mask;
            self.tnotes[9*k + i] &= mask;
            let box_col_idx = (k*3)%9 + (k/3)*27 + (j%3) + (j/3)*9;
            self.bnotes[box_col_idx] &= mask;
            // for box ´box_idx´
            self.notes[9*(i/3 + k/3)*3 + (j/3)*3 + k%3] &= mask;
            self.tnotes[9*(j/3 + k/3)*3 + (i/3)*3 + k%3] &= mask;
            self.bnotes[box_idx + k] &= mask;
        }
    }

    fn get_row(&self, i: usize) -> &[u8] {
        &self.board[i*9 .. i*9+9]
    }

    fn get_col(&self, i: usize) -> &[u8] {
        &self.tboard[i*9 .. i*9+9]
    }

    fn get_box(&self, i: usize) -> &[u8] {
        &self.bboard[i*9 .. i*9+9]
    }

    fn get_notes_row(&self, i: usize) -> &[u16] {
        &self.notes[i*9 .. i*9+9]
    }

    fn get_notes_col(&self, i: usize) -> &[u16] {
        &self.tnotes[i*9 .. i*9+9]
    }

    fn get_notes_box(&self, i: usize) -> &[u16] {
        &self.bnotes[i*9 .. i*9+9]
    }
}





fn main() {
    println!("Hello, world!");
}














// -------- plan ---------
// struct sudoku with:
// board: u8 array
// notes: u16 array
// 
// indexing using i, j

//
// method solve -> &[u8; 81]
// when one field is solved, return to start
// (maybe set preferred continuation unit)
// try hidden single
// try obvious singles
// ...
// bruteforce
// 
// 
// main:
// timing, correctness, printing
//
// obvious single -> bool
// check notes
// update field and notes
// return success?