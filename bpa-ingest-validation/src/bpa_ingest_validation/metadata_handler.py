import os


from .excel_wrapper import (
    ExcelWrapper,
    make_field_definition as fld,
    make_skip_column as skp,
)

from .util import make_logger
from .bpa_ingest_validations import ( get_date_isoformat,
extract_ands_id,
int_or_comment,
get_int,
)
import re
"""
class BaseDatasetControlContextual:
    metadata_patterns = [re.compile(r"^.*\.xlsx$")]
    sheet_names = [
        "Dataset Control",
    ]
    contextual_linkage = ()
    name_mapping = {}
    additional_fields = []

    def __init__(self, logger, path):
        self._logger = logger
        self._logger.info("dataset control path is: {}".format(path))
        #self.dataset_metadata = self._read_metadata(one(glob(path + "/*.xlsx")))

    def get(self, *context):
        if len(context) != len(self.contextual_linkage):
            self._logger.error(
                "Dataset Control context wanted %s does not match linkage %s"
                % (repr(context), repr(self.contextual_linkage))
            )
            return {}
        if context in self.dataset_metadata:
            self._logger.info("Dataset Control metadata found for: %s" % repr(context))
            return self.dataset_metadata[context]
        return {}

    def _coerce_ands(self, name, value):
        if name in (
            "sample_id",
            "library_id",
            "dataset_id",
            "bpa_sample_id",
            "bpa_library_id",
            "bpa_dataset_id",
            "bioplatforms_sample_id",
            "bioplatforms_library_id",
            "bioplatforms_dataset_id",
        ):
            return ingest_utils.extract_ands_id(self._logger, value)
        return value

    def _read_metadata(self, fname):
        # Obligatory fields
        field_spec = [
            fld(
                "access_control_date",
                "access_control_date",
                coerce=ingest_utils.date_or_int_or_comment,
            ),
            fld("access_control_reason", "access_control_reason"),
            fld("related_data", "related_data"),
        ]

        # Add any additional fields
        field_spec.extend(self.additional_fields)

        # ID fields used for linkage, add if present in linkage
        # Handle some data types using prepending bpa_ to the linkage fields
        # todo: make sure the linkage is a set at this point
        if len(
            set(self.contextual_linkage).intersection(
                {
                    "bpa_sample_id",
                    "bpa_library_id",
                    "bpa_dataset_id",
                    "bioplatforms_sample_id",
                    "bioplatforms_library_id",
                    "bioplatforms_dataset_id",
                },
            )
        ):
            for field in (
                "bpa_sample_id",
                "bpa_library_id",
                "bpa_dataset_id",
                "bioplatforms_sample_id",
                "bioplatforms_library_id",
                "bioplatforms_dataset_id",
            ):
                if field in self.contextual_linkage:
                    field_spec.append(
                        fld(
                            field,
                            field,
                            coerce=ingest_utils.extract_ands_id,
                        )
                    )
        else:
            for field in ("sample_id", "library_id", "dataset_id"):
                if field in self.contextual_linkage:
                    field_spec.append(
                        fld(
                            field,
                            field,
                            coerce=ingest_utils.extract_ands_id,
                        )
                    )

        dataset_metadata = {}
        for sheet_name in self.sheet_names:
            wrapper = ExcelWrapper(
                self._logger,
                field_spec,
                fname,
                sheet_name=sheet_name,
                header_length=1,
                column_name_row_index=0,
                suggest_template=True,
            )
            for error in wrapper.get_errors():
                self._logger.error(error)

            name_mapping = self.name_mapping

            for row in wrapper.get_all():
                context = tuple(
                    [
                        self._coerce_ands(v, row._asdict().get(v, None))
                        for v in self.contextual_linkage
                    ]
                )
                # keys not existing in row to create linkage
                if None in context:
                    continue

                if context in dataset_metadata:
                    raise Exception(
                        "duplicate ids for linkage {}: {}".format(
                            repr(self.contextual_linkage), repr(context)
                        )
                    )

                dataset_metadata[context] = row_meta = {}
                for field in row._fields:
                    value = getattr(row, field)
                    if field in self.contextual_linkage:
                        continue
                    row_meta[name_mapping.get(field, field)] = value
        return dataset_metadata

    def filename_metadata(self, *args, **kwargs):
        return {}
"""

# This was previously name BaseLibraryContextual (but it is really SAMPLE metadata)
#todo: change to GenericSampleContextual
class BaseSampleContextual:
    sheet_names = ["Sample metadata", "sample_metadata"]

    name_mapping = {
        "decimal_longitude": "longitude",
        "decimal_latitude": "latitude",
        "klass": "class",
    }
    metadata_unique_identifier = "bioplatforms_sample_id"

    field_spec = [
        fld(
            "bioplatforms_sample_id",
            "bioplatforms_sample_id",
            coerce=extract_ands_id,
        ),
        # sample_ID
        fld(
            "sample_id",
            "sample_id",
        ),
        fld("specimen_custodian", "specimen_custodian", optional=True),
        # specimen_ID
        fld("specimen_id", re.compile(r"specimen_?[Ii][Dd]")),
        # specimen_ID_description
        fld("specimen_id_description", re.compile(r"specimen_?[Ii][Dd]_description")),
        fld("sample_custodian", "sample_custodian"),
        fld("sample_type", "sample_type"),
        # sample_ID_description
        fld("sample_id_description", re.compile(r"sample_?[Ii][Dd]_description")),
        fld("sample_collection_type", "sample_collection_type"),
        fld("tissue", "tissue"),
        # tissue_preservation
        fld("tissue_preservation", "tissue_preservation"),
        fld("tissue_preservation_temperature", "tissue_preservation_temperature"),
        # sample_quality
        fld("sample_quality", "sample_quality"),
        fld("collection_permit", "collection_permit"),
        fld("identified_by", "identified_by"),
        fld("env_broad_scale", "env_broad_scale"),
        fld("env_local_scale", "env_local_scale"),
        fld("env_medium", "env_medium"),
        fld("altitude", "altitude"),
        fld("depth", "depth", coerce=int_or_comment),
        fld("temperature", "temperature"),
        fld("location_info_restricted", "location_info_restricted"),
        fld("genotypic_sex", "genotypic_sex"),
        fld("phenotypic_sex", "phenotypic_sex", optional=True),
        fld("method_sex_determination", "method_sex_determination", optional=True),
        fld("sex_certainty", "sex_certainty", optional=True),
        # taxon_id
        fld("taxon_id", re.compile(r"taxon_[Ii][Dd]"), coerce=get_int),
        # phylum
        fld("phylum", "phylum"),
        # class
        fld("klass", "class"),
        # order
        fld("order", "order"),
        # family
        fld("family", "family"),
        # genus
        fld("genus", "genus"),
        # species
        fld("species", "species"),
        fld("sub_species", "sub_species"),
        fld("scientific_name", "scientific_name"),
        fld("scientific_name_note", "scientific_name_note"),
        fld("scientific_name_authorship", "scientific_name_authorship"),
        # common_name
        fld("common_name", "common_name"),
        # collection_date
        fld(
            "collection_date",
            "collection_date",
            coerce=get_date_isoformat,
        ),
        # collector
        fld("collector", "collector"),
        # collection_method
        fld("collection_method", "collection_method"),
        # collector_sample_ID
        fld("collector_sample_id", re.compile(r"collector_sample_[Ii][Dd]")),
        # wild_captive
        fld("wild_captive", "wild_captive"),
        # source_population
        fld("source_population", "source_population"),
        # country
        fld("country", "country"),
        # state_or_region
        fld("state_or_region", "state_or_region"),
        # location_text
        fld("location_text", "location_text"),
        # habitat
        fld("habitat", "habitat"),
        # skip the private lat/long as this will contain data not to be shared
        skp("decimal_latitude_private"),
        skp("decimal_longitude_private"),
        # decimal_latitude
        fld("decimal_latitude", "decimal_latitude_public"),
        fld("decimal_latitude_public", "decimal_latitude_public"),
        # decimal_longitude
        fld("decimal_longitude", "decimal_longitude_public"),
        fld("decimal_longitude_public", "decimal_longitude_public"),
        # coord_uncertainty_metres
        fld("coord_uncertainty_metres", "coord_uncertainty_metres", optional=True),
        # life-stage
        fld("lifestage", re.compile("life[_-]stage")),
        # birth_date
        fld("birth_date", "birth_date", coerce=get_date_isoformat, optional=True),
        # death_date
        fld("death_date", "death_date", coerce=get_date_isoformat, optional=True),
        fld("health_state", "health_state"),
        # associated_media
        fld("associated_media", "associated_media"),
        # ancillary_notes
        fld("ancillary_notes", "ancillary_notes"),
        # taxonomic_group
        fld("taxonomic_group", "taxonomic_group"),
        # type_status
        fld("type_status", "type_status"),
        # material_extraction_type
        fld("material_extraction_type", re.compile(r"[Mm]aterial_extraction_type")),
        # material_extraction_date
        fld(
            "material_extraction_date",
            re.compile(r"[Mm]aterial_extraction_date"),
            coerce=get_date_isoformat,
        ),
        # material_extracted_by
        fld("material_extracted_by", re.compile(r"[Mm]aterial_extracted_by")),
        # material_extraction_method
        fld(
            "material_extraction_method",
            re.compile(r"[Mm]aterial_extraction_method"),
        ),
        # material_conc_ng_ul
        fld("material_conc_ng_ul", re.compile(r"[Mm]aterial_conc_ng_ul")),
        fld('indigenous_location', 'indigenous_location', optional=True),
        fld('isolate', 'isolate', optional=True),
        fld('host_common_name', 'host_common_name', optional=True),
        fld('host_family', 'host_family', optional=True),
        fld('host_scientific_name', 'host_scientific_name', optional=True),
        fld('host_organ', 'host_organ', optional=True),
        fld('host_symptom', 'host_symptom', optional=True),
        fld('host_status', 'host_status', optional=True),

    ]

    def __init__(self):
        self.logger = make_logger(__name__)
        pass

    def _read_metadata(self, fname):
        sample_metadata = {}

        wrapper = ExcelWrapper(
            self.logger,
            self.field_spec,
            fname,
            sheet_name=self.sheet_names,
            header_length=1,
            column_name_row_index=0,
            suggest_template=True,
            )
        for error in wrapper.get_errors():
            self.logger.error(error)

        for row in wrapper.get_all():
            sample_metadata = self.process_row(
                row, sample_metadata, os.path.basename(fname), wrapper.modified
            )

        return sample_metadata

    def process_row(self, row, sample_metadata, metadata_filename, metadata_modified):
        key_value = getattr(row, self.metadata_unique_identifier)
        if not key_value:
            return sample_metadata
        if key_value in sample_metadata:
            raise Exception(
                "duplicate {}: {}".format(self.metadata_unique_identifier, key_value)
            )
        sample_metadata[key_value] = row_meta = {}
        sample_metadata[key_value][
            "metadata_revision_date"
        ] = get_date_isoformat( metadata_modified)
        sample_metadata[key_value]["metadata_revision_filename"] = metadata_filename
        for field in row._fields:
            value = getattr(row, field)
            if field == self.metadata_unique_identifier:
                continue
            row_meta[self.name_mapping.get(field, field)] = value
        return sample_metadata
