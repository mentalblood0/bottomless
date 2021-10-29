local ARGV = {2, '1.*', '2.*', 'MSET', 6, '1.1.1', 'sone.one.one', '1.2', 'sone.two', '2', 'stwo'}

local keys_to_delete_patterns_number = tonumber(ARGV[1])
local keys_to_delete

for i,pattern in ipairs(ARGV) do

	if i > 1 then
	
		if i == (2 + keys_to_delete_patterns_number) then
			break
		end

        print('DEL', pattern)
		
		-- keys_to_delete = redis.call('keys', pattern)
		-- print('DEL', unpack(keys_to_delete))
	
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
					print(command, table.unpack(args))
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

print(command, table.unpack(args))