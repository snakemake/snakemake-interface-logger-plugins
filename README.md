# Snakemake Logger Plugin Interface

A base class for creating custom logging plugins for Snakemake.

## Usage

To use this base class, inherit from `LoggerPluginBase` and implement the `create_handler` method. The handler should be fully configured with a formatter and filter, as Snakemake will apply its defaults if these are not provided.

## License

This project is licensed under the MIT License.
