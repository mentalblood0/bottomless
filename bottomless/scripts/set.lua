local keys_to_delete_patterns_number = tonumber(ARGV[1])
local keys_to_delete

for i,pattern in ipairs(ARGV) do

	if i > 1 then
	
		if i == (2 + keys_to_delete_patterns_number) then
			break
		end
		
		keys_to_delete = redis.call('keys', pattern)
		if keys_to_delete[1] then
			redis.call('DEL', unpack(keys_to_delete))
		end

	end

end

local command = false
local N = false
local n = 1
local args = {}

for i,key in ipairs(ARGV) do
	if i >= (2 + keys_to_delete_patterns_number) then
		if command then
			if N == false then
				N = tonumber(key)+1
			else
				if n ~= N then
					args[n] = key
					n = n+1
				else
					redis.call(command, unpack(args))
					command = key
					N = false
					n = 1
					args = {}
				end
			end
		else
			command = key
		end
	end
end

redis.call(command, unpack(args))