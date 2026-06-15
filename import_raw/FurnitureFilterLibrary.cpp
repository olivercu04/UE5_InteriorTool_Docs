#include "FurnitureFilterLibrary.h"
#include "Engine/DataAsset.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "AssetRegistry/IAssetRegistry.h"

TArray<UPrimaryDataAsset*> UFurnitureFilterLibrary::FilterFurnitureItems(
    const TArray<UPrimaryDataAsset*>& AllItems,
    const FString& SearchText,
    const FString& FolderPath,
    const FName& CategoryFilter,
    int32 MaxResults)
{
    TArray<UPrimaryDataAsset*> Results;
    Results.Reserve(MaxResults > 0 ? FMath::Min(MaxResults, AllItems.Num()) : AllItems.Num());

    const bool bFilterBySearch = !SearchText.IsEmpty();
    const bool bFilterByFolder = !FolderPath.IsEmpty();
    const bool bFilterByCategory = !CategoryFilter.IsNone() && CategoryFilter != FName("All");

    for (UPrimaryDataAsset* Item : AllItems)
    {
        if (!Item) continue;

        bool bPassSearch = true;
        if (bFilterBySearch)
        {
            FTextProperty* VieNameProp = FindFProperty<FTextProperty>(Item->GetClass(), FName("VieName"));
            if (VieNameProp)
            {
                FText VieNameValue = VieNameProp->GetPropertyValue_InContainer(Item);
                bPassSearch = VieNameValue.ToString().Contains(SearchText, ESearchCase::IgnoreCase);
            }
        }
        if (!bPassSearch) continue;

        bool bPassFolder = true;
        if (bFilterByFolder)
        {
            FStrProperty* FolderProp = FindFProperty<FStrProperty>(Item->GetClass(), FName("MeshFolderPath"));
            if (FolderProp)
            {
                FString FolderValue = FolderProp->GetPropertyValue_InContainer(Item);
                bPassFolder = FolderValue.Contains(FolderPath, ESearchCase::IgnoreCase);
            }
        }
        if (!bPassFolder) continue;

        bool bPassCategory = true;
        if (bFilterByCategory)
        {
            FNameProperty* CategoryProp = FindFProperty<FNameProperty>(Item->GetClass(), FName("Category"));
            if (CategoryProp)
            {
                FName CategoryValue = CategoryProp->GetPropertyValue_InContainer(Item);
                bPassCategory = (CategoryValue == CategoryFilter);
            }
        }
        if (!bPassCategory) continue;

        Results.Add(Item);
        if (MaxResults > 0 && Results.Num() >= MaxResults) break;
    }

    return Results;
}

TArray<FSoftObjectPath> UFurnitureFilterLibrary::FilterFurnitureItemsFromRegistry(
    const FString& AssetPath,
    const FString& SearchText,
    const FString& FolderPath,
    const FName& CategoryFilter,
    int32 MaxResults)
{
    TArray<FSoftObjectPath> Results;

    IAssetRegistry& AssetRegistry = FModuleManager::LoadModuleChecked<FAssetRegistryModule>(TEXT("AssetRegistry")).Get();

    FARFilter Filter;
    Filter.PackagePaths.Add(FName(*AssetPath));
    Filter.bRecursivePaths = true;
    Filter.bRecursiveClasses = true;
    Filter.ClassPaths.Add(FTopLevelAssetPath(TEXT("/Script/Engine"), TEXT("Blueprint")));

    TArray<FAssetData> AssetList;
    AssetRegistry.GetAssets(Filter, AssetList);

    const bool bFilterBySearch = !SearchText.IsEmpty();
    const bool bFilterByFolder = !FolderPath.IsEmpty();
    const bool bFilterByCategory = !CategoryFilter.IsNone() && CategoryFilter != FName("All");

    for (const FAssetData& AssetData : AssetList)
    {
        if (bFilterByFolder)
        {
            FString PackagePath = AssetData.PackagePath.ToString();
            if (!PackagePath.Contains(FolderPath, ESearchCase::IgnoreCase))
                continue;
        }

        UObject* LoadedObj = AssetData.GetAsset();
        if (!LoadedObj) continue;

        UPrimaryDataAsset* DA = Cast<UPrimaryDataAsset>(LoadedObj);
        if (!DA) continue;

        if (bFilterBySearch)
        {
            FTextProperty* VieNameProp = FindFProperty<FTextProperty>(DA->GetClass(), FName("VieName"));
            if (VieNameProp)
            {
                FText VieNameValue = VieNameProp->GetPropertyValue_InContainer(DA);
                if (!VieNameValue.ToString().Contains(SearchText, ESearchCase::IgnoreCase))
                    continue;
            }
        }

        if (bFilterByCategory)
        {
            FNameProperty* CategoryProp = FindFProperty<FNameProperty>(DA->GetClass(), FName("Category"));
            if (CategoryProp)
            {
                FName CategoryValue = CategoryProp->GetPropertyValue_InContainer(DA);
                if (CategoryValue != CategoryFilter)
                    continue;
            }
        }

        Results.Add(AssetData.ToSoftObjectPath());
        if (MaxResults > 0 && Results.Num() >= MaxResults) break;
    }

    return Results;
}

TArray<FName> UFurnitureFilterLibrary::FilterMaterialItems(
    UDataTable* MaterialTable,
    const FString& SearchText,
    const TArray<FString>& TypeTags,
    const FString& SubFolderPath,
    int32 MaxResults)
{
    TArray<FName> Results;
    if (!MaterialTable) return Results;

    Results.Reserve(MaxResults > 0 ? MaxResults : 200);

    const bool bFilterBySearch = !SearchText.IsEmpty();
    const bool bFilterByType = TypeTags.Num() > 0;
    const bool bFilterBySubFolder = !SubFolderPath.IsEmpty();

    const UScriptStruct* RowStruct = MaterialTable->GetRowStruct();
    if (!RowStruct) return Results;

    // Blueprint struct (UUserDefinedStruct) luu property name co GUID append
    // → dung PropertyLink de tim theo keyword thay vi FindFProperty truc tiep
    FStrProperty* FolderProp = nullptr;
    FTextProperty* VieNameProp = nullptr;
    FTextProperty* EngNameProp = nullptr;

    for (FProperty* Prop = RowStruct->PropertyLink; Prop; Prop = Prop->PropertyLinkNext)
    {
        FString PropName = Prop->GetName();
        if (!FolderProp && PropName.Contains(TEXT("MaterialFolderPath"), ESearchCase::IgnoreCase))
            FolderProp = CastField<FStrProperty>(Prop);
        else if (!VieNameProp && PropName.Contains(TEXT("VieName"), ESearchCase::IgnoreCase))
            VieNameProp = CastField<FTextProperty>(Prop);
        else if (!EngNameProp && PropName.Contains(TEXT("EngName"), ESearchCase::IgnoreCase))
            EngNameProp = CastField<FTextProperty>(Prop);
    }

    const TMap<FName, uint8*>& RowMap = MaterialTable->GetRowMap();

    for (const auto& Pair : RowMap)
    {
        if (MaxResults > 0 && Results.Num() >= MaxResults) break;

        const FName& RowName = Pair.Key;
        const uint8* RowData = Pair.Value;

        // Loc theo TypeTags — MaterialFolderPath phai chua it nhat 1 tag
        if (bFilterByType && FolderProp)
        {
            FString FolderValue = FolderProp->GetPropertyValue_InContainer(RowData);
            bool bMatchAny = false;
            for (const FString& Tag : TypeTags)
            {
                if (FolderValue.Contains(Tag, ESearchCase::IgnoreCase))
                {
                    bMatchAny = true;
                    break;
                }
            }
            if (!bMatchAny) continue;
        }

        // Loc theo SubFolderPath (khi user drill vao sub-folder)
        if (bFilterBySubFolder && FolderProp)
        {
            FString FolderValue = FolderProp->GetPropertyValue_InContainer(RowData);
            if (!FolderValue.Contains(SubFolderPath, ESearchCase::IgnoreCase))
                continue;
        }

        // Loc theo search text (match VieName hoac EngName)
        if (bFilterBySearch)
        {
            bool bMatchSearch = false;
            if (VieNameProp)
            {
                FText VieValue = VieNameProp->GetPropertyValue_InContainer(RowData);
                if (VieValue.ToString().Contains(SearchText, ESearchCase::IgnoreCase))
                    bMatchSearch = true;
            }
            if (!bMatchSearch && EngNameProp)
            {
                FText EngValue = EngNameProp->GetPropertyValue_InContainer(RowData);
                if (EngValue.ToString().Contains(SearchText, ESearchCase::IgnoreCase))
                    bMatchSearch = true;
            }
            if (!bMatchSearch) continue;
        }

        Results.Add(RowName);
    }

    return Results;
}

UPrimaryDataAsset* UFurnitureFilterLibrary::LoadFurnitureItem(const FSoftObjectPath& ItemPath)
{
    UObject* LoadedObj = ItemPath.TryLoad();
    return Cast<UPrimaryDataAsset>(LoadedObj);
}
