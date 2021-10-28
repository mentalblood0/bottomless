-- local ARGV = {'1.*', 'DEL', 1, '1', 'MSET', 2, '1', 'sone'}

-- local command = false
-- local N = false
-- local n = 1
-- local args = {}

-- for i,key in ipairs(ARGV) do
-- 	if i ~= 1 then
-- 		if command then
-- 			if N == false then
-- 				N = tonumber(key)+1
-- 			else
-- 				if n ~= N then
-- 					args[n] = key
-- 					n = n+1
-- 				else
-- 					print(command, table.unpack(args))
-- 					command = key
-- 					N = false
-- 					n = 1
-- 					args = {}
-- 				end
-- 			end
-- 		else
-- 			command = key
-- 		end
-- 	end
-- end

-- print(command, table.unpack(args))

local t = {}
print(t[1] or true)