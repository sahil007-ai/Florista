"""
Per-product expressive content for /products/<slug>.html pages.

Why this file exists
--------------------
generate_product_pages.py used to template the same generic 2-paragraph
description into every product page — same opening sentence, same
wire-frame line, same MOQ paragraph. Read five pages back to back and
they felt identical. No personality, no voice, no Florista lingering
after the buyer scrolled away.

This module is the single source of truth for the *expressive* copy
that gets rendered on each product page: the narrative, what the piece
is built for, what it pairs with, a tactile note about the craft, and
a warm product-specific contact hook that anchors the WhatsApp CTA.

How to author
-------------
Each entry in CONTENT_BY_SLUG follows the schema in `_PRODUCT_FIELDS`
below. Keep the voice consistent:
  - direct, honest, practical (no "luxurious experiences await you")
  - Indian wedding context (mandap, sangeet, mehndi, baraat)
  - sensory but specific (gauge, layer count, minutes-per-piece)
  - one warm contact moment per product, never templated

Products without an entry here fall back to the generic template strings
in generate_product_pages.py so the build never breaks if a new SKU is
added before its copy is written.
"""
from __future__ import annotations
from typing import Any


# Schema (informational; not enforced at runtime — the generator
# tolerates partial entries via .get() with fallbacks).
_PRODUCT_FIELDS = (
    "narrative",       # list[str]: 2-3 paragraphs, the story / mood / why this piece
    "built_for",       # list[str]: 3-4 product-specific use-case bullets
    "pairs_with",      # str: one-sentence layering recommendation
    "craft_note",      # str: short tactile/process detail unique to this piece
    "hook_headline",   # str: warm, specific headline for the contact block
    "contact_hook",    # str: 1-2 sentences inviting a WhatsApp chat about THIS product
)


CONTENT_BY_SLUG: dict[str, dict[str, Any]] = {

    # ── Organza Flowers ───────────────────────────────────────────────

    "12-inch-regular-ornela": {
        "narrative": [
            "The smallest flower in our lineup and, by some margin, the "
            "most-ordered. The 12&quot; Regular &amp; Ornela is the piece "
            "that scatters across a setup like punctuation &mdash; a "
            "comma here, a full stop there &mdash; turning a sparse "
            "backdrop into a complete one.",
            "At 30 cm across it disappears into corners and lets the "
            "bigger flowers carry the focal weight. Eleven pastel "
            "shades, MOQ 10. Easy to over-order without hurting the "
            "margin on a single event &mdash; and that's exactly the "
            "math most decor partners run.",
        ],
        "built_for": [
            "Aisle markers and pew ends at intimate weddings.",
            "Filler clusters between larger 24\" &ndash; 36\" focal flowers on backdrops.",
            "Candy-bar facades, dessert tables, cake-table accents.",
            "Welcome-board frames and entrance-pillar trim.",
        ],
        "pairs_with":
            "Most installations buy 30 &ndash; 50 of these alongside 8 &ndash; 12 of the "
            "24\" Wedding Touch &mdash; the big flowers anchor the eye, the 12\" "
            "fill the negative space.",
        "craft_note":
            "Two layers of organza on a 16-gauge wire frame. Light enough "
            "to glue-gun straight onto fabric without sag, sturdy enough "
            "to survive packing and a four-event week.",
        "hook_headline": "Filling a 12-foot backdrop?",
        "contact_hook":
            "Tell us the backdrop dimensions and your two anchor sizes &mdash; "
            "we'll work out roughly how many 12\" you'll need to fill cleanly "
            "without crowding.",
    },

    "18-inch-lumora": {
        "narrative": [
            "The stepping-stone size. Bigger than filler, smaller than "
            "focal &mdash; the 18\" Lumora is the one buyers reach for when "
            "a wall has 24\" flowers but the eye keeps catching on empty "
            "patches between them.",
            "Eleven shades, all pastel-leaning. Holds shape on a vertical "
            "pillar even in light Nagpur breezes &mdash; the wire frame is "
            "bent in three directions during assembly so the petals "
            "don't flatten under their own weight.",
        ],
        "built_for": [
            "Mandap pillars and wedding entry archways.",
            "Mid-layer between 12\" filler and 24\"+ focal pieces.",
            "Ceiling drops over sangeet and reception stages.",
            "Photo-corner installations at receptions.",
        ],
        "pairs_with":
            "Layer the 18\" Lumora with 24\" Wedding Touch and a few 12\" "
            "fillers for a three-tier organza backdrop that reads as full "
            "from the first row to the last.",
        "craft_note":
            "Petals are individually steam-shaped before assembly, so each "
            "flower has a slightly different curl &mdash; cluster five "
            "together and the wall feels handmade instead of stamped.",
        "hook_headline": "Stuck between 12\" and 24\"?",
        "contact_hook":
            "Send a photo of the wall or pillar and the size of your big "
            "flowers &mdash; we'll suggest an 18\" count that closes the gaps "
            "without making it feel busy.",
    },

    "24-inch-wedding-touch": {
        "narrative": [
            "The workhorse. More 24\" Wedding Touch leaves our Nagpur "
            "factory than any other size we make &mdash; the proportion that "
            "reads &quot;wedding&quot; instantly without dominating a "
            "small room.",
            "Thirteen shades to choose from, including the two ivory "
            "variants couples keep coming back for. At 24 inches, you "
            "can stagger five across a 10-foot backdrop and it looks "
            "deliberate, not sparse.",
        ],
        "built_for": [
            "Intimate wedding backdrops (50 &ndash; 150 guests).",
            "Sangeet stage perimeters and photo-booth walls.",
            "Dessert-table and cake-table focal pieces.",
            "Reception entrance archways.",
        ],
        "pairs_with":
            "The classic combo &mdash; 6 to 10 of these on a 12-foot wall, "
            "with 18\" Lumora layered behind and 12\" fillers in the gaps. "
            "Most of our intimate-wedding orders look exactly like that.",
        "craft_note":
            "14-gauge spine, four layers of organza pleated by hand. Each "
            "one takes about 35 minutes on the factory floor &mdash; which is "
            "why we keep this size in steady stock instead of making to order.",
        "hook_headline": "Planning your first wedding-scale order?",
        "contact_hook":
            "Share your venue size and shade palette &mdash; we'll send a "
            "starter mix that lands at MOQ-friendly numbers and gives you "
            "a feel for the range before you scale up.",
    },

    "24-inch-premium-collection": {
        "narrative": [
            "Same 24-inch silhouette as the Wedding Touch, but printed and "
            "finished for premium-format bookings &mdash; corporate galas, "
            "five-star hotel weddings, the receptions where photographers "
            "ask about the flowers before they ask about the cake.",
            "Twenty shades and prints, several with a subtle metallic "
            "sheen that catches stage lighting. Priced higher than the "
            "standard 24\" because the fabric is upgraded and the print "
            "process is closer to textile printing than craft printing.",
        ],
        "built_for": [
            "Premium-finish wedding stages and gala dinners.",
            "Corporate event backdrops and brand-launch walls.",
            "Five-star hotel banquet decor.",
            "Designer-led photo-shoot installations.",
        ],
        "pairs_with":
            "Most premium bookings combine 8 &ndash; 12 of these with 1 &ndash; 2 of our "
            "36\"/40\" focal pieces for a layered hero wall. A 60/40 mix "
            "of Premium and Wedding Touch hits the right price/finish balance.",
        "craft_note":
            "Sheer organza printed in small runs. We cap each shade at "
            "80 pieces a month to keep the print register clean &mdash; if "
            "a buyer needs more in the same shade, we schedule a fresh "
            "print pass instead of stretching the run.",
        "hook_headline": "Have a brand palette to match?",
        "contact_hook":
            "Send the brand colour codes or a swatch image &mdash; we'll tell "
            "you which print shades match and whether a custom pass makes "
            "sense for your volume.",
    },

    "28-inch-wedding-bloom": {
        "narrative": [
            "A step up from the standard 24\" without committing to the "
            "32\" &ndash; 36\" stage-piece range. The 28\" Wedding Bloom is the "
            "size that fills a reception backdrop where 24\" looks small "
            "and 32\" looks heavy.",
            "Twelve shades, slightly deeper saturation than the 24\" "
            "line &mdash; works well under warm tungsten venue lighting "
            "where lighter pastels can wash out and disappear on camera.",
        ],
        "built_for": [
            "Mid-tier wedding backdrops for 200 &ndash; 400 guest receptions.",
            "Reception stage centerpieces and head-table walls.",
            "Engagement and ring-ceremony focal pieces.",
            "Hotel ballroom photo backdrops.",
        ],
        "pairs_with":
            "Five to seven of these as the primary layer, with 18\" &ndash; 24\" "
            "stepping in around the edges. Most 12-foot reception walls "
            "need around six of these to feel furnished.",
        "craft_note":
            "At 28 inches the petal weight starts to matter &mdash; we use a "
            "stiffer organza grade here so the bottom petals don't fold "
            "inward under their own weight after a day of warming on stage.",
        "hook_headline": "Stuck between 24\" and 36\"?",
        "contact_hook":
            "Tell us your stage width and ceiling height &mdash; we'll show "
            "you the visual difference 4 inches makes at your specific "
            "venue scale before you commit.",
    },

    "32-inch-pure-bliss": {
        "narrative": [
            "First of the statement sizes. At 32 inches, one flower "
            "carries an entire panel of a backdrop &mdash; three or four are "
            "all you need across a 14-foot mandap front.",
            "Gradient shading on the inner petals is hand-painted, not "
            "printed, so each piece is slightly unique. Couples who love "
            "it usually point at the tonal depth before they comment on "
            "the size.",
        ],
        "built_for": [
            "Wedding stage focal panels and large mandap fronts.",
            "Reception head-table walls (200+ guests).",
            "Sangeet and cocktail-night feature walls.",
            "Photo-shoot installations needing one or two anchor flowers.",
        ],
        "pairs_with":
            "The 32\" Pure Bliss usually plays solo &mdash; three across a "
            "backdrop with 18\"/24\" filling around. Layering more than "
            "four of these starts competing for attention.",
        "craft_note":
            "Hand-painted petal centres mean no two ship identical. We "
            "photograph each piece before packing, so buyers see exactly "
            "what's coming instead of guessing from a stock image.",
        "hook_headline": "Ready for a centerpiece moment?",
        "contact_hook":
            "Pick a backdrop reference image and we'll match the gradient "
            "shade to your venue lighting &mdash; incandescent halls and "
            "LED-lit ones need different undertones to read the same on camera.",
    },

    "36-inch-premium-blooms": {
        "narrative": [
            "Three feet of organza in one piece. The 36\" Premium Blooms "
            "is the size couples reach for when &quot;elegant&quot; needs "
            "to register from across a banquet hall &mdash; this is the one "
            "your guests photograph from their seats.",
            "Fourteen shades, with stronger saturation than the smaller "
            "sizes because at this scale a pastel reads as cream from 30 "
            "feet away. The 91 cm diameter holds proportion against "
            "eight-foot-plus stage backgrounds.",
        ],
        "built_for": [
            "Stage focal points at 250+ guest weddings.",
            "Mandap centre pieces and sehra-style backdrops.",
            "Reception entrance hero pieces.",
            "Corporate stage decor for ballroom-scale events.",
        ],
        "pairs_with":
            "One 36\" anchors a panel; three across a 16-foot backdrop "
            "reads symmetric without crowding. Most buyers pair with "
            "matching 18\" &ndash; 24\" in the same palette to layer outward.",
        "craft_note":
            "The 36\" frame is welded, not bent &mdash; at this size, hand-bent "
            "wire flexes during shipping. Welded joints add 8 minutes per "
            "unit but eliminate post-transit reshape work at the venue.",
        "hook_headline": "Want to see the scale before you order?",
        "contact_hook":
            "Send your venue floor plan or a stage photo with measurements "
            "&mdash; we'll mock the placement to scale, so you can see how "
            "three 36\"s sit before approving the quote.",
    },

    "40-inch-decor-blooms": {
        "narrative": [
            "Big-stage territory. Above this size the weight starts to "
            "matter for hanging installations, but at 40 inches the "
            "structure is still light enough to mount on standard "
            "backdrop frames without reinforcement.",
            "Thirteen shades, all chosen to perform under stage lighting "
            "&mdash; washed-out pastels are deliberately absent here because "
            "they vanish on camera once warm spots hit them.",
        ],
        "built_for": [
            "Wedding stage fronts and large mandap installations.",
            "Concert-style sangeet stages and DJ-night decor.",
            "Hotel ballroom focal walls.",
            "Convention-floor brand-event backdrops.",
        ],
        "pairs_with":
            "The 40\" works as the lowest layer of a three-size wall &mdash; "
            "40\" anchor at six-foot height, 28\"/32\" mid-band, 18\"/24\" "
            "trimming the top. Tells the eye where to rest first.",
        "craft_note":
            "Inner petal cluster uses a denser organza grade so the "
            "centre doesn't look hollow when stage lighting hits it from "
            "above. Subtle &mdash; but it's the difference between a flower "
            "that glows and one that flattens.",
        "hook_headline": "Designing a stage you want photographed?",
        "contact_hook":
            "Tell us the lighting setup &mdash; warm tungsten, cool LED, mixed "
            "&mdash; and we'll point you to the two or three shades from this "
            "range that hold colour fidelity under your specific lighting.",
    },

    "44-inch-majestic": {
        "narrative": [
            "The grand-event flower. Reserved for venues where a 36\" "
            "piece looks polite &mdash; we make these in smaller runs "
            "because most weddings genuinely don't need this scale.",
            "Thirteen shades, leaning toward the deeper end of the "
            "palette. At this size the petal layering is what separates "
            "a Florista 44\" from a generic large flower &mdash; eight "
            "overlapping layers, hand-set, instead of the typical four.",
        ],
        "built_for": [
            "Grand-stage destination weddings.",
            "Oversized photo-backdrop walls for 500+ guest events.",
            "Ballroom centerpieces in 30-foot-ceiling venues.",
            "Art-installation decor and fashion-runway sets.",
        ],
        "pairs_with":
            "Two 44\" Majestics carry an entire stage. Most buyers go "
            "single-piece-bold &mdash; flanked by 24\"/28\" stepping outward &mdash; "
            "rather than ordering three or more.",
        "craft_note":
            "Eight-layer petal construction means each flower takes about "
            "90 minutes on the floor. We schedule these on the same day "
            "to keep colour batching consistent within an order &mdash; small "
            "detail, big visual difference.",
        "hook_headline": "This isn't a default order &mdash; talk to us first.",
        "contact_hook":
            "Share the venue and the look you're chasing &mdash; we'll honestly "
            "tell you whether 44\" is the right call for your space, or "
            "whether two 36\"s and proper layering will look better at the "
            "same budget.",
    },

    "48-inch-big-flora": {
        "narrative": [
            "Four feet of organza, MOQ dropped to 5 because we know "
            "nobody orders ten of these at once. Made for venues where "
            "the ceiling is high enough that 36\" looks small.",
            "Thirteen shades, all stage-finish quality. The petal frame "
            "is reinforced at the spine so the flower keeps a perfect "
            "circular outline even when wall-mounted at an angle.",
        ],
        "built_for": [
            "Massive reception backdrops at destination weddings.",
            "Hotel atrium and pre-function-area focal pieces.",
            "Five-star ballroom stage installations.",
            "Corporate gala and award-show stage walls.",
        ],
        "pairs_with":
            "One or two 48\"s set the focal points; everything else in the "
            "installation should be 24\" or smaller to maintain hierarchy. "
            "Three 48\"s on one wall start fighting each other.",
        "craft_note":
            "Reinforced spine adds about 15 minutes per piece in assembly. "
            "Buyers who've used cheaper 4-foot flowers from elsewhere "
            "usually bring up sag-after-mounting as their main complaint "
            "&mdash; that's the problem this construction step solves.",
        "hook_headline": "Going big? Let's plan the logistics first.",
        "contact_hook":
            "At this size, packing and shipping volume matter. Send your "
            "delivery city and event date &mdash; we'll quote landed cost and "
            "lead time before you confirm the design.",
    },

    "60-inch-giant-flora": {
        "narrative": [
            "Five feet across. Our largest flower, made on order for the "
            "events where ordinary wedding decor isn't the assignment. "
            "Most buyers who order the 60\" Giant Flora have a specific "
            "stage drawing in hand already.",
            "Thirteen shades. Built on a welded steel frame instead of "
            "wire &mdash; at 60 inches, wire bends under its own weight and "
            "the flower goes oval. Steel is heavier but holds true round "
            "through transport, mounting, and a multi-day event.",
        ],
        "built_for": [
            "Hero focal pieces at flagship weddings and 1000+ guest receptions.",
            "Statement walls at fashion shows, brand launches, and film sets.",
            "Single-flower stage installations and art-direction projects.",
            "Photo-op installations at celebrity events and luxury venues.",
        ],
        "pairs_with":
            "Almost always plays solo &mdash; one 60\" Giant Flora in the centre "
            "of the stage, with 24\"/18\" arranged outward in a halo "
            "pattern. Two of these in one room is rare and intentional.",
        "craft_note":
            "We finish each 60\" with a numbered tag and photograph it on "
            "a measured backdrop before crating. You see the actual flower "
            "you're getting &mdash; not a stock photo of a different one made "
            "last month.",
        "hook_headline": "This is a centrepiece. Treat it like one.",
        "contact_hook":
            "Tell us the event date, venue, and look you're after. We'll "
            "set up a WhatsApp video call with the piece on our factory "
            "floor before it ships &mdash; at this scale, last-minute "
            "surprises are the wrong kind of surprise.",
    },

    # ── Premium &amp; Specialty ─────────────────────────────────────────

    "glowing-flower-3ft": {
        "narrative": [
            "Three feet of organza wrapped around an internal LED rig. "
            "Switch it on after sunset and the Glowing Flower softens "
            "into a gentle glow &mdash; an entirely different presence from "
            "the daytime version.",
            "Two shades, both designed to play with both warm and cool "
            "LED. The battery pack is tucked into the spine and runs "
            "about six hours per charge &mdash; enough for an evening "
            "reception with margin to spare.",
        ],
        "built_for": [
            "Night sangeet, cocktail receptions, and after-sunset weddings.",
            "Outdoor venues where natural light fades mid-event.",
            "Premium themed parties &mdash; gala dinners, milestone birthdays.",
            "Photo backdrops at film and fashion events with low ambient light.",
        ],
        "pairs_with":
            "Three Glowing Flowers down the centre of a backdrop, with "
            "non-illuminated 24\" filling the perimeter, is the standard "
            "arrangement for night-time installations.",
        "craft_note":
            "The LED rig is replaceable &mdash; buyers using these across "
            "multiple events appreciate that batteries are user-serviceable "
            "instead of soldered in. We include a spare driver with every "
            "five-piece order.",
        "hook_headline": "Designing a night-time look?",
        "contact_hook":
            "Tell us your event time and ambient lighting &mdash; we'll match "
            "the LED warmth to the venue's existing lights, so the glow "
            "reads intentional instead of out of place.",
    },

    "aura-flower-3ft": {
        "narrative": [
            "Modern, structural, deliberately sparse. The Aura is a "
            "designer-floor flower &mdash; fewer petals, more architecture. "
            "It reads contemporary against any palette and pairs cleanly "
            "with metallic accents.",
            "Two shades to start. The structural form means one Aura "
            "does the work of three traditional flowers in a minimalist "
            "setup &mdash; most modern-aesthetic backdrops use only six to "
            "eight of these total.",
        ],
        "built_for": [
            "Modern wedding stages with minimalist art-direction.",
            "Luxury reception backdrops in design-forward venues.",
            "Boutique hotel events and private-villa weddings.",
            "Editorial and fashion-shoot installations.",
        ],
        "pairs_with":
            "The Aura works with negative space, not layered around. "
            "Place five or six in deliberate intervals across a wide "
            "backdrop &mdash; resist the impulse to fill the gaps with "
            "smaller sizes.",
        "craft_note":
            "The petal angle is set during a single hand-press so the "
            "structural form stays consistent across an order. Frees a "
            "full day on the production floor for batch &mdash; which is why "
            "we hold these to a 5-piece MOQ.",
        "hook_headline": "Going minimal?",
        "contact_hook":
            "Share your moodboard or a venue reference &mdash; we'll suggest "
            "an Aura count that respects the white space instead of "
            "trying to fill it.",
    },

    "tri-petal-flower-2-5ft": {
        "narrative": [
            "Three sculpted petals in a geometric arrangement &mdash; closer "
            "to a design object than a flower. Made for couples and event "
            "designers chasing a specific aesthetic, not a default look.",
            "Two shades. The geometric form catches uplighting in a way "
            "standard rounded flowers don't &mdash; angles cast shadows, and "
            "shadows give you depth on camera.",
        ],
        "built_for": [
            "Modern themed stages with architectural moodboards.",
            "Design-forward photo walls and gallery-style installations.",
            "Brand-launch and product-reveal stages.",
            "Avant-garde wedding sangeet and pre-wedding shoot decor.",
        ],
        "pairs_with":
            "Tri-Petals work best at intervals against a clean dark wall. "
            "Pair with 18\" or 24\" Wedding Touch in the same palette only "
            "if you want a softer reading &mdash; most installations use "
            "Tri-Petals alone.",
        "craft_note":
            "Each petal is shaped on a wooden mould, dried flat, then "
            "assembled. The geometric precision means we reject roughly "
            "one in eight off the floor for shape variance &mdash; that's why "
            "this piece doesn't show up on bulk-discount runs.",
        "hook_headline": "Want something different?",
        "contact_hook":
            "Send the look you're chasing &mdash; Pinterest board, sketch, "
            "AI-generated reference, anything. We'll tell you whether the "
            "Tri-Petal is the right move or whether a custom shape would "
            "land closer to your vision.",
    },

    "cinderella-flowers": {
        "narrative": [
            "Designed for the storybook brief. Layered petals, fairytale "
            "silhouette, finished with a pearl-tone centre. The "
            "Cinderella Flower is what couples request when their "
            "moodboard has phrases like &quot;princess&quot; and "
            "&quot;magical&quot;.",
            "Two shades to anchor &mdash; soft pink and ivory white. Both "
            "translate cleanly across film cameras and phone photography, "
            "which matters more for fairytale themes than people expect.",
        ],
        "built_for": [
            "Fairytale-themed weddings and engagement decor.",
            "Princess-themed birthday parties and milestone events.",
            "Enchanted-garden photo-booth installations.",
            "Bridal-shower and pre-wedding ritual backdrops.",
        ],
        "pairs_with":
            "Cinderella works in clusters &mdash; five or six close together "
            "rather than spread thin. Layer with a few 18\" Lumora in "
            "matching shades for a soft halo effect around the focal point.",
        "craft_note":
            "The pearl centre is hand-set with a tweezers, not glued from "
            "a tube. We use 3 mm faux pearls &mdash; large enough to catch "
            "light, small enough not to read costume.",
        "hook_headline": "Designing a fairytale moment?",
        "contact_hook":
            "Send the moodboard and the photographer's lighting style &mdash; "
            "we'll match the pearl tone to either film-warm or "
            "digital-cool, depending on what the camera will favour on the day.",
    },

    "fluffy-bloom": {
        "narrative": [
            "Soft, voluminous, almost cloud-like. The Fluffy Bloom trades "
            "sharp petal definition for tactile fullness &mdash; close-up "
            "shots show the texture, mid-range shots read as soft volume.",
            "Two shades. Lighter weight than a standard 24\" because the "
            "layering is designed to read full from any angle, not "
            "stacked in one direction.",
        ],
        "built_for": [
            "Soft pastel engagement and ring-ceremony backdrops.",
            "Baby-shower and gender-reveal decor.",
            "Boudoir and bridal-portrait shoots.",
            "Romantic-styled couple-shoot installations.",
        ],
        "pairs_with":
            "Fluffy Blooms layer beautifully with each other. Cluster "
            "four to six in a single tone for a tonal effect, or mix the "
            "two shades for soft contrast &mdash; both work cleanly.",
        "craft_note":
            "The volume comes from a six-layer petal construction nobody "
            "else makes at this price &mdash; most factories cap at four "
            "layers because the time investment doesn't fit a budget "
            "product. We keep the price low because volume is high.",
        "hook_headline": "Soft palette, big presence?",
        "contact_hook":
            "Tell us your shoot or event aesthetic &mdash; soft-pink, "
            "dusty-rose, ivory-cream &mdash; and we'll suggest the right shade "
            "ratio so the cluster reads cohesive instead of noisy.",
    },

    "premium-fabric-flowers": {
        "narrative": [
            "Structured fabric &mdash; not organza. Reads heavier, more "
            "defined, more architectural. Premium Fabric Flowers belong "
            "on the walls where every other element is also high-end.",
            "Five shades, all designed to hold colour under tungsten and "
            "LED stage lighting. Heavier than organza by weight, which "
            "matters for ceiling drops but is invisible on standard wall "
            "mounts.",
        ],
        "built_for": [
            "High-end wedding stages and luxury-venue receptions.",
            "Corporate event walls and brand-experiential installations.",
            "Gallery-style art-direction shoots.",
            "Premium hotel ballroom centerpieces.",
        ],
        "pairs_with":
            "Premium Fabric works alongside our Aura and Tri-Petal in "
            "modern installations, or with the Premium Collection 24\" "
            "for a unified high-end organza-meets-fabric wall.",
        "craft_note":
            "Each fabric flower is cut, pleated, and steamed on a "
            "five-step process line &mdash; about 50 minutes per piece. The "
            "structure holds shape across multiple events without "
            "re-shaping, which is the value buyers pay for.",
        "hook_headline": "Building a high-end installation?",
        "contact_hook":
            "Send the venue brief and the spend ceiling &mdash; we'll work "
            "backwards from your wall dimensions and tell you how many "
            "fabric flowers vs. organza fillers gets you the look without "
            "overshooting budget.",
    },

    "blooming-dales": {
        "narrative": [
            "One design, three sizes &mdash; 24, 32, and 36 inches. Made for "
            "layered installations where you want unified visual language "
            "across a multi-tier backdrop.",
            "Four shades, available across all three sizes. Buyers "
            "building tiered backdrops usually order in roughly a 1:2:1 "
            "ratio (large : medium : small) and adjust by venue.",
        ],
        "built_for": [
            "Multi-tier reception and sangeet backdrops.",
            "Layered photo-walls with single-design consistency.",
            "Phased installations across multiple event nights.",
            "Decor partners building reusable inventory.",
        ],
        "pairs_with":
            "Blooming Dales is itself a layering kit &mdash; keep the "
            "installation within the family for a clean consistent read, "
            "or mix with 18\" Lumora for an extra outer layer.",
        "craft_note":
            "Same petal pattern at three scales means the shape language "
            "stays consistent across the wall. Most multi-size flowers "
            "from other manufacturers shift petal count or layering "
            "across sizes, and the wall reads inconsistent. Ours doesn't.",
        "hook_headline": "Building reusable decor inventory?",
        "contact_hook":
            "If you're a decor partner, talk to us about volume slabs "
            "across the size mix &mdash; we structure pricing differently for "
            "inventory-building orders versus single-event orders.",
    },

    "printed-fabric-flower": {
        "narrative": [
            "Vibrant prints on structured fabric &mdash; colour and pattern "
            "in one piece. Designed for themed events and photo walls "
            "where the flower itself is part of the visual statement.",
            "Four prints to start, each independently developed. The "
            "print register is sharp enough to hold up under close "
            "inspection, which matters for photo-heavy events.",
        ],
        "built_for": [
            "Themed birthday and milestone-event walls.",
            "Festival-themed weddings &mdash; Holi, Onam, harvest receptions.",
            "Brand-experiential and pop-up event installations.",
            "Vibrant photo-walls for social-media-led events.",
        ],
        "pairs_with":
            "Printed Fabric Flowers carry their own visual weight &mdash; "
            "pair with solid-shade 24\" Wedding Touch in a complementary "
            "colour to give the eye a place to rest between prints.",
        "craft_note":
            "Prints are pre-tested under three lighting conditions "
            "(natural, tungsten, LED) before we approve a run. We've "
            "killed two prints at sample stage because they shifted hue "
            "too far under warm light &mdash; the print catalogue you see is "
            "the survivor list.",
        "hook_headline": "Themed event in mind?",
        "contact_hook":
            "Share the theme and target audience &mdash; we'll suggest a "
            "print mix that fits the moodboard and tell you when a "
            "custom print run makes sense for your volume.",
    },

    # ── Theme &amp; Events ──────────────────────────────────────────────

    "organza-butterfly": {
        "narrative": [
            "Butterflies, not flowers &mdash; but built on the same handcrafted "
            "organza process. The piece kids' party planners reach for "
            "when standard floral decor doesn't match the brief.",
            "Two shades currently, both designed to mix freely. Mounted "
            "with magnetic backing on request so they can be reset "
            "across multiple party rooms without tape damage.",
        ],
        "built_for": [
            "Kids' birthdays, baby showers, and christening parties.",
            "Pre-school and children-focused brand events.",
            "Whimsical wedding mehndi and haldi decor.",
            "Photo-booth and dessert-table accent installations.",
        ],
        "pairs_with":
            "Mix Organza Butterflies with 12\" Regular &amp; Ornela for a "
            "&quot;scattered garden&quot; look &mdash; butterflies among the "
            "flowers, instead of clusters of either alone.",
        "craft_note":
            "Wing veining is hand-drawn with a fine-tip brush &mdash; about "
            "six minutes per butterfly. We've kept it manual because the "
            "slight variance is what makes a wall of these look organic "
            "instead of mass-produced.",
        "hook_headline": "Planning a kids' or whimsical-themed event?",
        "contact_hook":
            "Tell us the age group and event date &mdash; we'll suggest "
            "mounting options (magnetic, adhesive, hanging) that suit "
            "your venue and let you reset the decor between rooms.",
    },

    "dream-wings-90-inch": {
        "narrative": [
            "Seven and a half feet of angel wing in a single piece. A "
            "photo prop, not decor &mdash; Dream Wings exist for the moment "
            "someone stands in front of them and gets photographed.",
            "Two shades, both designed to read clean against either "
            "white or dark backgrounds. The wing structure is foldable "
            "for transport and opens to full span on assembly at the venue.",
        ],
        "built_for": [
            "Hero photo-prop installations at weddings and engagements.",
            "Brand events and Instagrammable activations.",
            "Theme-night and milestone-birthday entrances.",
            "Editorial photoshoots and content-creator setups.",
        ],
        "pairs_with":
            "Dream Wings stand alone &mdash; they're the focal piece of the "
            "room, not a layered element. Keep surrounding decor minimal "
            "so the wings carry the visual weight uncontested.",
        "craft_note":
            "Foldable structure means a 90-inch wing fits a 36 &times; 24 "
            "inch shipping crate. Five-minute on-site assembly with two "
            "people. We've shipped these to Mumbai, Bangalore, Delhi, and "
            "Goa without damage in the last 18 months.",
        "hook_headline": "Want THE photo of the night?",
        "contact_hook":
            "Tell us the venue and event format &mdash; we'll talk you "
            "through assembly logistics, recommend lighting placement for "
            "the photo moment, and confirm delivery timing so the wings "
            "arrive a clear day ahead of the event.",
    },

    "theme-party-fish": {
        "narrative": [
            "Fabric fish for under-the-sea parties &mdash; kids' birthdays "
            "where the brief is &quot;mermaids and ocean&quot; and a "
            "flower won't do. Built on the same handcrafted process as "
            "the rest of the catalogue.",
            "Four shades and patterns, all designed to mix in a single "
            "installation. Hangs from fishing line for the floating-school "
            "effect, or wall-mounts directly.",
        ],
        "built_for": [
            "Mermaid-themed and under-the-sea birthday parties.",
            "Children's swim-school and aquarium-event decor.",
            "Beach-themed pre-wedding shoots and mehndi events.",
            "Hotel kids'-club and family-event installations.",
        ],
        "pairs_with":
            "Theme Party Fish layer beautifully with our Organza "
            "Butterflies for a fantasy-creature mash-up &mdash; fish floating "
            "below, butterflies above &mdash; common at twin-themed "
            "siblings' joint parties.",
        "craft_note":
            "Fishing-line mounts are pre-attached to the dorsal seam &mdash; "
            "the buyer just hangs and adjusts height. Saves about an "
            "hour of on-site setup per dozen, which adds up at a "
            "50-piece kids'-party install.",
        "hook_headline": "Ocean-themed event coming up?",
        "contact_hook":
            "Send the venue ceiling height and how many kids &mdash; we'll "
            "suggest a fish count and mount style that creates the "
            "floating-school effect without overwhelming a smaller room.",
    },

}


# ── The Florista Promise ────────────────────────────────────────────
#
# This block is identical across every product page. Same on purpose:
# it's the brand-identity through-line that ties all 22 pages together,
# the same way every Apple product page says "Designed by Apple in
# California." Edit here and every page picks it up on the next run.
FLORISTA_PROMISE = (
    "Direct from our Nagpur factory floor &mdash; no middlemen, no "
    "inflated retail markup. Every flower is hand-cut, hand-pleated, "
    "and hand-finished by the same artisan team that has been making "
    "decor since 2018. Bulk pricing, honest MOQs, PAN India shipping."
)


# Standard reassurance strip rendered under every contact hook.
HOOK_REASSURANCE = (
    "Made in Nagpur. Shipped PAN India. WhatsApp replies usually under "
    "30 minutes during business hours."
)
