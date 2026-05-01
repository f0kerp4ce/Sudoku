use std::{fmt, fs, env};
use std::time::Instant;

#[derive(Debug, Clone)]
struct Sudoku {
    board: [u8; 81], // regular, contains correct solution after bruteforce
    tboard: [u8; 81], // column major stored
    bboard: [u8; 81], // box major stored

    notes: [u16; 81],
    tnotes: [u16; 81],
    bnotes: [u16; 81],

    lm_row: usize,
    lm_col: usize,
}
// box major: (boxes & inside boxes)
// 0 1 2
// 3 4 5
// 6 7 8

impl Default for Sudoku {
    fn default() -> Self {
        Self { board: [0; 81], tboard: [0; 81], bboard: [0; 81], notes: [0; 81], tnotes: [0; 81], bnotes: [0; 81], lm_col: 0, lm_row: 0 }
    }
}

impl fmt::Display for Sudoku {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        for i in 0..81 {
            if i%27 == 0 {writeln!(f, "\n").expect("issue with writeln!");}
            else if i%9 == 0 {writeln!(f, "").expect("issue with writeln!");}
            else if i%3 == 0 {write!(f, " ").expect("issue with write!");}
            write!(f, "{}", self.board[i]).expect("could not write a field of the sudoku");
        }
        Ok(())
    }
}

impl Sudoku {
    fn new_from_path(path: String) -> Self {
        let mut s: Sudoku = Sudoku::default();
        s.read_from_path(path);
        s
    }

    fn read_from_path(&mut self, path: String) {
        let contents = fs::read_to_string(path)
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

    fn init_notes2(&mut self) {
        self.notes = [1022; 81];
        self.tnotes = [1022; 81];
        self.bnotes = [1022; 81];

        for i in 0..81 {
            if self.board[i] != 0 {
                self.notes[i] = 0;
            }
            if self.tboard[i] != 0 {
                self.tnotes[i] = 0;
            }
            if self.bboard[i] != 0 {
                self.bnotes[i] = 0;
            }

            let row = self.get_row(i/9);
            let col = self.get_col(i%9);
            let block = self.get_box(((i/3)%3) + (i/27)*3);
            let mut poss = self.notes[i];
            if poss != 0 {
                for j in 0..9 {
                    poss &= !(1u16 << row[j]);
                    poss &= !(1u16 << col[j]);
                    poss &= !(1u16 << block[j]);
                }
                self.notes[i] = poss;
                self.tnotes[(i%9)*9 + i/9] &= poss;
                self.bnotes[(i/27 + (i%9)/3) * 9 + i%3 +((i/9)%3)*3];
            }
        }
    }

    fn init_notes(&mut self) {
        self.notes = [1022; 81];
        self.tnotes = [1022; 81];
        self.bnotes = [1022; 81];

        for i in 0..9 {
            for j in 0..9 {
                let curr = self.board[i*9 + j];
                //if curr == 0 {continue}
                // clear notes for fields that are already present
                if self.board[9*i+j] != 0 {
                    self.notes[9*i+j] = 0;
                }
                if self.tboard[9*i+j] != 0 {
                    self.tnotes[9*i+j] = 0;
                }
                if self.bboard[9*i+j] != 0 {
                    self.bnotes[9*i+j] = 0;
                }
                
                let mask = !(1u16 << curr); // e.g. curr = 3  =>  mask = 0b..11110111
                let box_idx = j/3 + (i/3)*3;
                let bi = (i/3)*3;
                let bj = (j/3)*3;
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
                    self.notes[9*(bi + k/3) + bj + k%3] &= mask;
                    self.tnotes[9*(bj + k/3)+ bi + k%3] &= mask;
                    self.bnotes[9*box_idx + k] &= mask;
                }
            }
        }
    }

    fn solve(&mut self) -> bool {
        while !self.check() {
            // maybe add preferred next units
            if self.obvious_single_after_insert(self.lm_col, self.lm_row) {continue}
            if self.obvious_single() {continue}
            if self.hidden_single() {continue}

            // else bruteforce
            return self.bruteforce();
        }
        true
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
            curr &= curr-1;
        }
        
        
        false
    }

    fn obvious_single(&mut self) -> bool {
        // check each row, col and block and find fields where only one number is possible
        for i in 0..9 {
            let notes_row = self.get_notes_row(i);
            let notes_col = self.get_notes_col(i);
            let notes_block = self.get_notes_box(i);
            
            // check if there is only one possibility
            for j in 0..9 {
                if notes_row[j].count_ones() == 1 {
                    self.set(i, j, notes_row[j].trailing_zeros() as u8);
                    return true;
                }
                else if notes_col[j].count_ones() == 1 {
                    self.set(j, i, notes_col[j].trailing_zeros() as u8);
                    return true;
                }
                else if notes_block[j].count_ones() == 1 {
                    // 'i' is block number; 'j' is position inside block
                    // we want new_i := row number and new_j := col number
                    self.set((i/3)*3 + j/3, (i%3)*3 + j%3, notes_block[j].trailing_zeros() as u8);
                    return true;
                }
            }
        }
        false // no obvious single exists
    }

    fn obvious_single_after_insert(&mut self, row: usize, col: usize) -> bool {
        let notes_row = self.get_notes_row(row);
        let notes_col = self.get_notes_col(col);
        let notes_block = self.get_notes_box((row/3)*3 + col%3);
        for j in 0..9 {
            if notes_row[j].count_ones() == 1 {
                self.set(row, j, notes_row[j].trailing_zeros() as u8);
                return true;
            }
            else if notes_col[j].count_ones() == 1 {
                self.set(j, col, notes_col[j].trailing_zeros() as u8);
                return true;
            }
            else if notes_block[j].count_ones() == 1 {
                // 'j' is position inside block
                // we want new_i := row number and new_j := col number
                self.set((row/3)*3 + j/3, (col/3)*3 + j%3, notes_block[j].trailing_zeros() as u8);
                return true;
            }
        }
        false
    }

    fn hidden_single(&mut self) -> bool {
        let changed = vec![self.lm_row, self.lm_col]; // maybe add boxes
        for i in changed.into_iter().chain(0..9) {
            let notes_row = self.get_notes_row(i);
            let notes_col = self.get_notes_col(i);
            let notes_block = self.get_notes_box(i);
            // array [u16; 9] where appearance in field i is 1 for each field, number
            
            // check if there is only one possibility for a number
            let mut row_counts = [0u16; 10];
            let mut col_counts = [0u16; 10];
            let mut block_counts = [0u16; 10];

            for n in 1..10 {
                // count occurences of 'n'
                let mask = 1<<n;
                for j in 0..9 {
                    row_counts[n] += (notes_row[j] & mask) >> n;
                    col_counts[n] += (notes_col[j] & mask) >> n;
                    block_counts[n] += (notes_block[j] & mask) >> n;
                }
                // check if there is a number with only one occurence
                if row_counts[n] == 1 {
                    // find which field is the hidden single
                    for j in 0..9 {
                        let masked_row = notes_row[j] & mask;
                        if masked_row != 0 {
                            self.set(i, j, masked_row.trailing_zeros() as u8);
                            return true;
                        }
                    }
                }
                if col_counts[n] == 1 {
                    for j in 0..9 {
                        let masked_col = notes_col[j] & mask;
                        if masked_col != 0 {
                            self.set(j, i, masked_col.trailing_zeros() as u8);
                            return true;
                        }
                    }
                }
                if block_counts[n] == 1 {
                    for j in 0..9 {
                        let masked_block = notes_block[j] & mask;
                        if masked_block != 0 {
                            // i is block number, j is number within block
                            self.set((i/3)*3 + j/3, (i%3)*3 + j%3, masked_block.trailing_zeros() as u8);
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
        self.notes[i*9 + j] = 0; // delete notes for this field
        self.tboard[j*9 + i] = v;
        self.tnotes[j*9 + i] = 0;
        let single_box_idx: usize = (i*3)%9 + (i/3)*27 + (j%3) +(j/3)*9;
        self.bboard[single_box_idx] = v;
        self.bnotes[single_box_idx] = 0;

        let box_idx = (i/3)*3 + (j/3); // 0..9

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
            self.notes[((i/3)*3 + k/3)*9 + ((j/3)*3 + k%3)] &= mask;
            self.tnotes[((j/3)*3 + k/3)*9 +((i/3)*3 + k%3)] &= mask;
            self.bnotes[9 * box_idx + k] &= mask;
        }
        self.lm_row = i;
        self.lm_col = j;
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
    let args: Vec<String> = env::args().collect();
    if args.len() < 4 {
        eprintln!("Usage: {} <path> <n> <version>", args[0]);
        std::process::exit(1);
    }

    let path = &args[1];
    let n: u32 = args[2].parse().expect("n must be a valid integer");
    let version: i32 = args[3].parse().expect("version must be a valid integer");

    println!("path: {}", path);
    println!("n: {}", n);
    println!("version: {}", version);

    // Read the grid once to avoid file I/O during the benchmarking loop
    let initial_grid = Sudoku::new_from_path(path.to_string());
    
    // We will store the result of the final run to check correctness and print
    let mut final_grid = initial_grid.clone();
    
    let mut total_ns: u128 = 0;

    for _ in 0..n {
        // Create a fresh copy for the solver, matching the C implementation
        let mut grid_copy = initial_grid.clone();
        
        let start = Instant::now();
        // Since the current Rust code has one solve version, we just call it directly. 
        // If you implement a second algorithm later, you can branch on `version` here.
        grid_copy.solve(); 
        let elapsed = start.elapsed();
        
        total_ns += elapsed.as_nanos();
        final_grid = grid_copy; 
    }

    let succ = final_grid.check();

    // Print results
    println!("LANGUAGE:RUST");
    
    // Printing the solution as a flat array to mimic a typical pretty_print_sol 
    print!("SOLUTION:");
    for val in final_grid.board.iter() {
        print!("{}", val);
    }
    println!();
    
    println!("SUCCESS:{}", if succ { "TRUE" } else { "FALSE" });
    println!("MEAN_TIME_NS:{}", total_ns / (n as u128));
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