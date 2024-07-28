import hashlib

bit_vector = [0] * 10000

sha = hashlib.sha256()
md5 = hashlib.md5()

with open('pokedex.txt', 'rb') as store:
    lines = store.readlines()
    for poke in lines:
        sha.update(poke)
        sha_val = sha.hexdigest()
        sha_val = int(sha_val, 16) % 10000
        # print(sha_val)
        bit_vector[sha_val] = 1
        md5.update(poke)
        md5_val = md5.hexdigest()
        md5_val = int(md5_val, 16) % 10000
        # print(md5_val)
        bit_vector[md5_val] = 1
    store.close()
total_probs = 0
total_finds = 0
with open('new_finds.txt', 'rb') as new_finds:
    pokemons = new_finds.readlines()
    for poke in pokemons:
        sha.update(poke)
        sha_val = sha.hexdigest()
        sha_val = int(sha_val, 16) % 1000
        # print(sha_val)
        total_finds+=1
        md5.update(poke)
        md5_val = md5.hexdigest()
        md5_val = int(md5_val, 16) % 1000
        # print(md5_val)
        pokemon = poke.decode('utf-8')
        # pokemon = pokemon[:-1]
        # print(pokemon)
        if bit_vector[sha_val] == 1 and bit_vector[md5_val] == 1:
            print( pokemon+"can be present in pokedex")
            total_probs+=1
        else:
            print(pokemon+"is NOT present in pokedex, it is a new pokemon")
    new_finds.close()
print("Total Collisions: "+str(total_probs))
print("Total Finds: "+str(total_finds))

