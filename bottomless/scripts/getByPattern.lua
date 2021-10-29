local keys = (redis.call('keys', ARGV[1]))
local values={}

for i,key in ipairs(keys) do 
	local val = redis.call('GET', key)
	values[i]=val
	i=i+1
end

local result = {}
result[1] = keys
result[2] = values

return result