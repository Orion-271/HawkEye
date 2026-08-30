import json
import os

from population import analyze_building


# ============================================================
# FILES
# ============================================================

INPUT_FILE = "buildings.json"
OUTPUT_FILE = "enriched_buildings.json"


# ============================================================
# CHECK INPUT FILE
# ============================================================

if not os.path.exists(INPUT_FILE):

    print()
    print("==============================")
    print("ERROR")
    print("==============================")
    print()

    print(
        f"Could not find: {INPUT_FILE}"
    )

    print()
    print("Files currently in this folder:")

    for filename in os.listdir("."):
        print(" -", filename)

    raise SystemExit


# ============================================================
# LOAD JSON
# ============================================================

try:

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        buildings = json.load(file)

except json.JSONDecodeError as error:

    print()
    print("==============================")
    print("ERROR: INVALID JSON")
    print("==============================")
    print()

    print(error)

    raise SystemExit


# ============================================================
# CHECK DATA FORMAT
# ============================================================

if not isinstance(buildings, list):

    print()
    print("==============================")
    print("ERROR: WRONG JSON FORMAT")
    print("==============================")
    print()

    print(
        "The JSON file must contain a list of buildings."
    )

    raise SystemExit


# ============================================================
# START
# ============================================================

print()
print("==============================")
print("REAL BUILDING POPULATION TEST")
print("==============================")

print(
    "Buildings found:",
    len(buildings)
)

print()


# ============================================================
# PROCESS BUILDINGS
# ============================================================

processed_buildings = []

successful = 0
skipped = 0
failed = 0


for index, building in enumerate(
    buildings,
    start=1
):

    building_id = building.get(
        "id",
        f"Building_{index}"
    )

    print(
        f"[{index}/{len(buildings)}] Processing {building_id}..."
    )


    # --------------------------------------------------------
    # CHECK GPS
    # --------------------------------------------------------

    if (
        "latitude" not in building
        or
        "longitude" not in building
    ):

        print(
            "   SKIPPED - GPS coordinates missing"
        )

        skipped += 1

        processed_buildings.append(
            building
        )

        print()

        continue


    # --------------------------------------------------------
    # CHECK AREA
    # --------------------------------------------------------

    if "area_m2" not in building:

        print(
            "   SKIPPED - area_m2 missing"
        )

        skipped += 1

        processed_buildings.append(
            building
        )

        print()

        continue


    # --------------------------------------------------------
    # PREPARE BUILDING
    # --------------------------------------------------------

    building_for_analysis = (
        building.copy()
    )

    building_for_analysis[
        "area"
    ] = building[
        "area_m2"
    ]


    # --------------------------------------------------------
    # QUERY WORLDPOP
    # --------------------------------------------------------

    try:

        result = analyze_building(
            building_for_analysis
        )


        # ----------------------------------------------------
        # PRESERVE ORIGINAL DATA
        # ----------------------------------------------------

        building_result = (
            building.copy()
        )


        # Add population results

        building_result[
            "population_density"
        ] = result[
            "population_density"
        ]

        building_result[
            "estimated_population"
        ] = result[
            "estimated_population"
        ]


        # ----------------------------------------------------
        # DISPLAY RESULT
        # ----------------------------------------------------

        print(
            "   Latitude:",
            building[
                "latitude"
            ]
        )

        print(
            "   Longitude:",
            building[
                "longitude"
            ]
        )

        print(
            "   Area:",
            building[
                "area_m2"
            ],
            "m²"
        )

        print(
            "   Population density:",
            round(
                result[
                    "population_density"
                ],
                2
            ),
            "people/km²"
        )

        print(
            "   Estimated population exposure:",
            round(
                result[
                    "estimated_population"
                ],
                2
            ),
            "people"
        )


        processed_buildings.append(
            building_result
        )

        successful += 1


    except Exception as error:

        print(
            "   ERROR:",
            error
        )

        failed += 1

        processed_buildings.append(
            building
        )


    print()


# ============================================================
# SAVE OUTPUT
# ============================================================

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        processed_buildings,
        file,
        indent=4
    )


# ============================================================
# SUMMARY
# ============================================================

print("==============================")
print("COMPLETE")
print("==============================")

print(
    "Total buildings:",
    len(buildings)
)

print(
    "Successfully processed:",
    successful
)

print(
    "Skipped:",
    skipped
)

print(
    "Failed:",
    failed
)

print()

print(
    "Results saved to:"
)

print(
    os.path.abspath(
        OUTPUT_FILE
    )
)

print("==============================")