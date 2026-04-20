#[derive(Debug)]
struct Sudoku {
    board: [u8; 81], // regular
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

    fn solve(&mut self) {
        loop {
            if self.obvious_single() {continue}
        }
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
        false
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