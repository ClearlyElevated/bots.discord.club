def get_avatar_url(avatar_hash, user_id, discri):
    if avatar_hash is None or avatar_hash == "":
        return f"https://cdn.discordapp.com/embed/avatars/{int(discri) % 5}.png"

    elif str(avatar_hash).startswith("a_"):
        return f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.gif"

    else:
        return f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.png"