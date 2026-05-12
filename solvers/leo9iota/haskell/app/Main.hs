module Main where -- declare main mod

import System.Environment (getArgs) -- import getArgs fn from system stdlib

main :: IO ()
main = do
  args <- getArgs -- get cli args
  case args of
    [path, nStr, solverIdxStr] -> do
      putStrLn $ "path: " ++ path
      putStrLn $ "n: " ++ nStr
      putStrLn $ "solver: " ++ solverIdxStr
    _ -> putStrLn "usage: haskell-solver <PATH> <N> <SOLVER_IDX>"
