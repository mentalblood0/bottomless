-- exists(key)
-- note that key exists if it or it's subkeys ({key}.*) exists in terms of redis



local value = redis.call('GET', ARGV[1])
local subkeys = (redis.call('KEYS', ARGV[1] .. '.*'))

return value or subkeys[1]