-- getByPattern(pattern)



local keys = redis.call('keys', ARGV[1])
local values = {}

for i,key in ipairs(keys) do
	values[i] = redis.call('GET', key)
end

local result = {}
result[1] = keys
result[2] = values

return result