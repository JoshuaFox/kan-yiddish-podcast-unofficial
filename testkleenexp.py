import re
import ke


search_str = "xxxbbcccbeeeeeeeeebxxx"

greedy_kleenexp = ke.search('["b" [1+  #any ] "b"]', search_str, ).group(0)
greedy_regexp = re.search(r'b.+b', search_str, ).group(0)

nongreedy_kleenexp = ke.search('["b" [1+:fewest #any] "b"]', "%s" % search_str, ).group(0)
nongreedy_regexp = re.search(r'b.+?b', search_str, ).group(0)

assert greedy_regexp == greedy_kleenexp, f"{greedy_regexp}!={greedy_kleenexp}"
assert nongreedy_regexp != greedy_regexp, f"{nongreedy_regexp}=={greedy_regexp}"

# fails
assert nongreedy_regexp == nongreedy_kleenexp, f"{nongreedy_regexp}!={nongreedy_kleenexp}"
# fails
assert nongreedy_kleenexp != greedy_kleenexp, f"{nongreedy_kleenexp}=={greedy_kleenexp}"
