from src.agroiq_demo import SoilInput, analyze, result_to_dict


def main() -> None:
    sample = SoilInput(
        red=162.3,
        green=202.9,
        blue=230.7,
        reaction_time_sec=600,
        sample_temperature_c=24.0,
        ph=8.1,
        ec_ds_m=1.8,
        moisture_percent=21.0,
        soil_temperature_c=22.5,
        nitrogen_indicator=44.0,
        sensor_phosphorus_indicator=9.0,
        potassium_indicator=168.0,
        crop="Paxta",
        field_area_ha=10.0,
    )
    result = result_to_dict(analyze(sample))
    print("AgroIQ competition demonstration\n")
    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
