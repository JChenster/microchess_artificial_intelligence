all:
	echo "Making files..."
	echo #/bin!/bash" > MicroChessGeneticAlgorithm;
	echo "pypy3 genetic_algorithm.py \"\$$@\"" >> MicroChessGeneticAlgorithm
	chmod u+x MicroChessGeneticAlgorithm

	cat info.txt
	./MicroChessGeneticAlgorithm 16 10 .02 250 .9 1
	rm ./MicroChessGeneticAlgorithm
clean:
	rm MicroChessGeneticAlgorithm
	
