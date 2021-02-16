"""Implementation of Hamming and Edit distance"""

from sys import maxsize

class Hamming():
	"""Class holding two methods: dist() and closest()"""
	@classmethod
	def dist(cls, str1: str, str2: str) -> int:
		"""Calculates the edit distance between two strings.
		*str1* String A
		*str2* String B
		"""
		m = len(str1)
		n = len(str2)
		dp = [[0 for x in range(n + 1)] for y in range(m + 1)]
		for i in range(m + 1):
			for j in range(n + 1):
				if i == 0:
					dp[i][j] = j
				elif j == 0:
					dp[i][j] = i
				elif str1[i-1] == str2[j-1]:
					dp[i][j] = dp[i-1][j-1]
				else:
					dp[i][j] = 1 + min(dp[i][j-1], dp[i-1][j], dp[i-1][j-1])
		return dp[m][n]

	@classmethod
	def closest(cls, name: str, targets: list) -> list:
		"""Calculates the string with the shortest edit distance.
		*name* the original string.
		*targest* a list of desired strings.
		"""
		val = maxsize
		idx = -1
		for i, row in enumerate(targets):
			d = cls.dist(name, row[0])
			if d < val:
				val = d
				idx = i
		return targets[idx]
