# Utopia 1

| Field      | Value |
|------------|-------|
| Category   | OSINT |
| Points     | 50 |
| Solves     | 167 |

## Description

johnbuck69420 believes he is a big consipiracy theorist. His recent ramblings have been about a strange artist whose works supposedly predict the future. Most people think he's crazy but John insists otherwise. He believes that the artist is warning us about a new disease.

flag format: apoorvctf{artist'sName_diseaseName}

> author : Ellie

## Files

- [insta.png](./insta.png)
- [instapc1.png](./instapc1.png)
- [instapc2.png](./instapc2.png)

## Writeup

### Flag

```
apoorvctf{BlessonLal_blackiris}
```

### Executive Summary

Pure OSINT chain. The challenge points to an X (Twitter) account whose posts describe a plague-themed Instagram artist with a "rather strange name." Searching Instagram for misspelled plague-adjacent handles surfaces `@plauge_bunny_` (note the intentional typo — that's the strange name). The profile name is **Blesson Lal** and a March 5 post references **black iris**, giving both flag components.

### Solve Path

**Step 1 — Find the Twitter account**

The description names `@johnbuck69420` (John Buck), a self-proclaimed conspiracy theorist. His posts (around March 5, 2026) contain two key clues:
- *"I found this artist once on Instagram. I don't remember clearly, but a rather strange name."*
- *"This guy reminds me of Utopia, the comic/show. You know the one in which the comic predicts disease outbreaks before it actually happens."*

The Utopia reference frames the search: an artist whose work predicts a new disease / plague — matching the show's premise of a comic that foreshadows bioweapon outbreaks.

**Step 2 — Find the Instagram account**

Searching Instagram for plague/disease-themed artists with unusual handles leads to **`@plauge_bunny_`** — the deliberate misspelling of "plague" (plauge) is the "rather strange name" John vaguely remembered.

Profile: **Blesson Lal** — `@plauge_bunny_`

![Instagram profile](./insta.png)

**Step 3 — Identify the disease**

A post dated March 5, 2026 references **black iris** in the caption — plague-adjacent symbolism (black irises evoke death, black death, and omens), fitting the "warning about a new disease" angle from the challenge description.

![Post 1](./instapc1.png)
![Post 2](./instapc2.png)

**Step 4 — Construct the flag**

- Artist's name: `BlessonLal` (display name, spaces removed)
- Disease name: `blackiris` (Black Iris, lowercased and concatenated)

```
apoorvctf{BlessonLal_blackiris}
```


### Execution & Results


