-- pexpireByPattern(pattern, milliseconds, *extra_keys)



local keys = redis.call('keys', ARGV[1])

for i,key in ipairs(keys) do 
	redis.call('PEXPIRE', key, ARGV[2])
end

for i,key in ipairs(ARGV) do
    if i >= 3 then
        redis.call('PEXPIRE', key, ARGV[2])
    end
end